import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import database
from databases.interfaces import Record
from fastapi import HTTPException, status
from models.player import players
from models.battle import battles
from models.inventory import inventory
from RPG_OOP import (
    Player as RPGPlayer, create_enemy,
    Weapon, Armor, Potion
)

active_battles: dict[int, dict] = {}

PLAYER_BASE_HEALTH = 100
PLAYER_BASE_DAMAGE = 10
PLAYER_BASE_CRITICAL = 5
PLAYER_BASE_DEFENSE = 0


def _item_to_dict(item) -> dict:
    base = {
        "item_name": item.name,
        "rarity": item.rarity.name,
    }
    if isinstance(item, Weapon):
        base.update({"item_type": "weapon", "damage_bonus": item.damage_bonus, "crit_rate": item.crit_rate})
    elif isinstance(item, Armor):
        base.update({"item_type": "armor", "defense_bonus": item.defense_bonus})
    elif isinstance(item, Potion):
        base.update({"item_type": "potion", "heal": item.heal})
    return base


class BattleService:

    async def start_battle(self, player_id: int) -> dict:
        if player_id in active_battles:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Você já está em batalha. Termine ou fuja antes de iniciar outra.")

        row = await database.fetch_one(players.select().where(players.c.id == player_id))
        if not row:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personagem não encontrado.")

        if row["health"] <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seu personagem está morto. Use POST /players/revive para ressuscitar.")

        rpg_player = RPGPlayer(row["name"])
        rpg_player.health = row["health"]
        rpg_player.level = row["level"]
        rpg_player.damage = row["damage"]
        rpg_player.critical = row["critical"]
        rpg_player.defense = row["defense"]

        enemy = create_enemy(row["level"])

        active_battles[player_id] = {
            "player": rpg_player,
            "enemy": enemy,
            "damage_dealt": 0,
            "damage_taken": 0,
        }

        return {
            "message": f"Um {enemy.name} apareceu!",
            "enemy_name": enemy.name,
            "enemy_health": enemy.health,
            "enemy_damage": enemy.damage,
            "enemy_defense": enemy.defense,
            "player_health": rpg_player.health,
        }

    async def battle_action(self, player_id: int, action: str) -> dict:
        if player_id not in active_battles:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Nenhuma batalha ativa.")

        state = active_battles[player_id]
        rpg_player = state["player"]
        enemy = state["enemy"]

        if action == "flee":
            if random.random() < 0.4:
                del active_battles[player_id]
                return {
                    "message": "Você fugiu com sucesso!",
                    "player_health": rpg_player.health,
                    "enemy_health": enemy.health,
                    "result": "fled",
                }
            else:
                dmg = enemy.calculate_damage(rpg_player)
                rpg_player.take_damage(dmg)
                state["damage_taken"] += dmg

                if rpg_player.health <= 0:
                    await self._end_battle(player_id, "defeat")
                    return {
                        "message": f"Tentou fugir mas não conseguiu! {enemy.name} te deu o golpe final. Seu personagem morreu — use POST /players/revive para ressuscitar.",
                        "player_health": 0,
                        "enemy_health": enemy.health,
                        "result": "defeat",
                    }

                return {
                    "message": f"Não conseguiu fugir! {enemy.name} causou {dmg} de dano.",
                    "player_health": rpg_player.health,
                    "enemy_health": enemy.health,
                    "result": "ongoing",
                }

        # attack
        player_dmg = rpg_player.calculate_damage(enemy)
        enemy.take_damage(player_dmg)
        state["damage_dealt"] += player_dmg

        if enemy.health <= 0:
            loots = enemy.generate_drops()
            loot_names = [item.name for item in loots]

            for item in loots:
                d = _item_to_dict(item)
                await database.execute(inventory.insert().values(player_id=player_id, equipped=False, **d))

            await self._end_battle(player_id, "victory", loots)
            row = await database.fetch_one(players.select().where(players.c.id == player_id))

            return {
                "message": f"Você derrotou {enemy.name}! (+1 nível)",
                "player_health": row["health"],
                "enemy_health": 0,
                "result": "victory",
                "loot": loot_names,
                "level_up": True,
                "new_level": row["level"],
            }

        # contra-ataque
        enemy_dmg = enemy.calculate_damage(rpg_player)
        rpg_player.take_damage(enemy_dmg)
        state["damage_taken"] += enemy_dmg

        if rpg_player.health <= 0:
            await self._end_battle(player_id, "defeat")
            return {
                "message": f"Você causou {player_dmg} de dano, mas {enemy.name} contra-atacou e te derrotou! Use POST /players/revive para ressuscitar.",
                "player_health": 0,
                "enemy_health": enemy.health,
                "result": "defeat",
            }

        return {
            "message": f"Você causou {player_dmg} de dano. {enemy.name} contra-atacou com {enemy_dmg} de dano.",
            "player_health": rpg_player.health,
            "enemy_health": enemy.health,
            "result": "ongoing",
        }

    async def _end_battle(self, player_id: int, result: str, loots=None) -> None:
        state = active_battles.pop(player_id)
        rpg_player = state["player"]
        enemy = state["enemy"]

        loot_str = ", ".join(item.name for item in loots) if loots else None

        await database.execute(battles.insert().values(
            player_id=player_id,
            enemy_name=enemy.name,
            result=result,
            damage_dealt=state["damage_dealt"],
            damage_taken=state["damage_taken"],
            loot=loot_str,
        ))

        if result == "victory":
            row = await database.fetch_one(players.select().where(players.c.id == player_id))
            await database.execute(
                players.update().where(players.c.id == player_id).values(
                    health=rpg_player.health,
                    level=row["level"] + 1,
                    victories=row["victories"] + 1,
                )
            )
        elif result == "defeat":
            # Marca como morto (health = 0), limpa equipamentos
            await database.execute(
                players.update().where(players.c.id == player_id).values(
                    health=0,
                    weapon_name=None,
                    armor_name=None,
                )
            )
            # Apaga inventário inteiro ao morrer
            await database.execute(
                inventory.delete().where(inventory.c.player_id == player_id)
            )

    async def get_history(self, player_id: int) -> list[Record]:
        return await database.fetch_all(
            battles.select().where(battles.c.player_id == player_id).order_by(battles.c.created_at.desc())
        )
