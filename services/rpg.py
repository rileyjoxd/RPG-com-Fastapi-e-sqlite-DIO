import random
from databases.interfaces import Record
from fastapi import HTTPException, status

from database import database
from models.rpg import characters, battles, inventory
from RPG_OOP import Player, Weapon, Armor, Potion, Rarity, create_enemy, generate_loot

# Sessão em memória: battle_id -> { enemy, player_obj, char_db_id }
_active_battles: dict[int, dict] = {}


def _rarity_from_str(r: str) -> Rarity:
    return Rarity[r.upper()]


def _build_player_from_record(record: Record) -> Player:
    """Reconstrói um Player do RPG_OOP a partir do registro do banco."""
    p = Player(record["name"])
    p.health = record["health"]
    p.damage = record["damage"]
    p.defense = record["defense"]
    p.critical = record["critical"]
    p.level = record["level"]

    if record["weapon_name"]:
        p.weapon = Weapon(
            record["weapon_name"],
            record["weapon_damage"],
            record["weapon_crit"],
            Rarity.COMMON,
        )
    if record["armor_name"]:
        p.armor = Armor(
            record["armor_name"],
            record["armor_defense"],
            Rarity.COMMON,
        )
    return p


class RPGService:

    # ── Personagem ──────────────────────────────────────────────────

    async def get_character(self, user_id: int) -> Record:
        query = characters.select().where(characters.c.user_id == user_id)
        char = await database.fetch_one(query)
        if not char:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personagem não encontrado.")
        return char

    async def create_character(self, user_id: int, name: str) -> Record:
        exists = await database.fetch_one(
            characters.select().where(characters.c.user_id == user_id)
        )
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Você já tem um personagem.")

        cmd = characters.insert().values(
            user_id=user_id,
            name=name,
            health=100,
            damage=10,
            defense=0,
            critical=5,
            level=1,
            weapon_name=None,
            weapon_damage=0,
            weapon_crit=0,
            armor_name=None,
            armor_defense=0,
            is_alive=True,
        )
        char_id = await database.execute(cmd)
        return await database.fetch_one(characters.select().where(characters.c.id == char_id))

    # ── Inventário ───────────────────────────────────────────────────

    async def get_inventory(self, user_id: int) -> list[Record]:
        char = await self.get_character(user_id)
        query = inventory.select().where(inventory.c.character_id == char["id"])
        return await database.fetch_all(query)

    async def use_item(self, user_id: int, item_id: int) -> dict:
        char = await self.get_character(user_id)
        item = await database.fetch_one(
            inventory.select().where(
                (inventory.c.id == item_id) & (inventory.c.character_id == char["id"])
            )
        )
        if not item:
            raise HTTPException(status_code=404, detail="Item não encontrado.")
        if item["item_type"] != "potion":
            raise HTTPException(status_code=400, detail="Só poções podem ser usadas assim.")

        new_health = char["health"] + item["value"]
        await database.execute(
            characters.update().where(characters.c.id == char["id"]).values(health=new_health)
        )
        await database.execute(inventory.delete().where(inventory.c.id == item_id))
        return {"message": f"Você usou {item['item_name']} e ficou com {new_health} de vida."}

    async def equip_item(self, user_id: int, item_id: int) -> dict:
        char = await self.get_character(user_id)
        item = await database.fetch_one(
            inventory.select().where(
                (inventory.c.id == item_id) & (inventory.c.character_id == char["id"])
            )
        )
        if not item:
            raise HTTPException(status_code=404, detail="Item não encontrado.")

        if item["item_type"] == "weapon":
            await database.execute(
                characters.update().where(characters.c.id == char["id"]).values(
                    weapon_name=item["item_name"],
                    weapon_damage=item["value"],
                    weapon_crit=item["extra"],
                )
            )
            await database.execute(
                inventory.update().where(
                    (inventory.c.character_id == char["id"]) & (inventory.c.item_type == "weapon")
                ).values(equipped=False)
            )
        elif item["item_type"] == "armor":
            await database.execute(
                characters.update().where(characters.c.id == char["id"]).values(
                    armor_name=item["item_name"],
                    armor_defense=item["value"],
                )
            )
            await database.execute(
                inventory.update().where(
                    (inventory.c.character_id == char["id"]) & (inventory.c.item_type == "armor")
                ).values(equipped=False)
            )
        else:
            raise HTTPException(status_code=400, detail="Poções não podem ser equipadas.")

        await database.execute(
            inventory.update().where(inventory.c.id == item_id).values(equipped=True)
        )
        return {"message": f"{item['item_name']} equipado com sucesso."}

    # ── Batalha ──────────────────────────────────────────────────────

    async def start_battle(self, user_id: int) -> dict:
        char = await self.get_character(user_id)
        if not char["is_alive"]:
            raise HTTPException(status_code=400, detail="Seu personagem está morto. Crie um novo.")

        # Verifica batalha ativa
        for bid, session in _active_battles.items():
            if session["char_id"] == char["id"]:
                raise HTTPException(status_code=409, detail=f"Você já tem uma batalha ativa (id={bid}).")

        player = _build_player_from_record(char)
        enemy = create_enemy(char["level"])

        cmd = battles.insert().values(
            character_id=char["id"],
            enemy_name=enemy.name,
            enemy_health_start=enemy.health,
            result=None,
            rounds=0,
        )
        battle_id = await database.execute(cmd)

        _active_battles[battle_id] = {
            "char_id": char["id"],
            "player": player,
            "enemy": enemy,
        }

        return {
            "message": f"Um {enemy.name} apareceu!",
            "battle_id": battle_id,
            "enemy_name": enemy.name,
            "enemy_health": enemy.health,
            "character_health": player.health,
        }

    async def attack(self, user_id: int, battle_id: int) -> dict:
        session, char = await self._get_session(user_id, battle_id)
        player: Player = session["player"]
        enemy = session["enemy"]
        log = []

        # Jogador ataca
        dmg_player = player.calculate_damage(enemy)
        enemy.take_damage(dmg_player)
        log.append(f"{player.name} causou {dmg_player} de dano em {enemy.name}. (HP inimigo: {enemy.health})")

        # Inimigo morreu?
        if enemy.health <= 0:
            return await self._resolve_victory(user_id, battle_id, session, char, log)

        # Inimigo ataca
        dmg_enemy = enemy.calculate_damage(player)
        player.take_damage(dmg_enemy)
        log.append(f"{enemy.name} causou {dmg_enemy} de dano em {player.name}. (Seu HP: {player.health})")

        await self._increment_round(battle_id)

        # Jogador morreu?
        if player.health <= 0:
            return await self._resolve_defeat(battle_id, session, char, log)

        # Salva HP atualizado
        await database.execute(
            characters.update().where(characters.c.id == char["id"]).values(health=player.health)
        )

        return {
            "message": "Rodada concluída.",
            "log": log,
            "battle_id": battle_id,
            "enemy_health": enemy.health,
            "character_health": player.health,
            "result": "em_andamento",
        }

    async def flee(self, user_id: int, battle_id: int) -> dict:
        session, char = await self._get_session(user_id, battle_id)
        player: Player = session["player"]
        enemy = session["enemy"]
        log = []

        if random.random() < 0.4:
            log.append("Você fugiu com sucesso!")
            await self._end_battle(battle_id, "fuga", session, char, player)
            return {"message": "Fuga bem-sucedida.", "log": log, "result": "fuga"}

        # Falhou em fugir — inimigo ataca
        dmg = enemy.calculate_damage(player)
        player.take_damage(dmg)
        log.append(f"Não conseguiu fugir! {enemy.name} aproveitou e causou {dmg} de dano. (Seu HP: {player.health})")
        await self._increment_round(battle_id)

        if player.health <= 0:
            return await self._resolve_defeat(battle_id, session, char, log)

        await database.execute(
            characters.update().where(characters.c.id == char["id"]).values(health=player.health)
        )
        return {
            "message": "Fuga falhou.",
            "log": log,
            "battle_id": battle_id,
            "enemy_health": enemy.health,
            "character_health": player.health,
            "result": "em_andamento",
        }

    async def get_battle_history(self, user_id: int) -> list[Record]:
        char = await self.get_character(user_id)
        query = battles.select().where(battles.c.character_id == char["id"]).order_by(battles.c.id.desc())
        return await database.fetch_all(query)

    # ── Helpers privados ─────────────────────────────────────────────

    async def _get_session(self, user_id: int, battle_id: int):
        char = await self.get_character(user_id)
        session = _active_battles.get(battle_id)
        if not session or session["char_id"] != char["id"]:
            raise HTTPException(status_code=404, detail="Batalha não encontrada ou não pertence a você.")
        return session, char

    async def _increment_round(self, battle_id: int):
        await database.execute(
            battles.update().where(battles.c.id == battle_id).values(
                rounds=battles.c.rounds + 1
            )
        )

    async def _save_drops(self, char_id: int, drops: list) -> list[str]:
        drop_names = []
        for item in drops:
            item_type = "weapon" if isinstance(item, Weapon) else "armor" if isinstance(item, Armor) else "potion"
            value = item.damage_bonus if isinstance(item, Weapon) else item.defense_bonus if isinstance(item, Armor) else item.heal
            extra = item.crit_rate if isinstance(item, Weapon) else 0
            await database.execute(
                inventory.insert().values(
                    character_id=char_id,
                    item_name=item.name,
                    item_type=item_type,
                    rarity=item.rarity.name,
                    value=value,
                    extra=extra,
                    equipped=False,
                )
            )
            drop_names.append(f"{item.name} ({item.rarity.name})")
        return drop_names

    async def _resolve_victory(self, user_id, battle_id, session, char, log):
        player: Player = session["player"]
        enemy = session["enemy"]

        level_up = False
        new_level = char["level"] + 1
        level_up = True
        log.append(f"Você derrotou {enemy.name}! Subiu para o nível {new_level}!")

        # Drops do RPG_OOP
        drops_obj = enemy.generate_drops()
        drop_names = await self._save_drops(char["id"], drops_obj)
        if drop_names:
            log.append(f"Itens dropados: {', '.join(drop_names)}")

        # Baú (30% chance)
        chest_drops = []
        if random.random() < 0.3:
            num = random.randint(1, 3)
            chest_items = [generate_loot() for _ in range(num)]
            chest_drops = await self._save_drops(char["id"], chest_items)
            log.append(f"Você achou um baú! Itens: {', '.join(chest_drops)}")

        await self._end_battle(battle_id, "vitoria", session, char, player, new_level=new_level)

        return {
            "message": "Vitória!",
            "log": log,
            "result": "vitoria",
            "drops": drop_names + chest_drops,
            "level_up": level_up,
            "character_health": player.health,
        }

    async def _resolve_defeat(self, battle_id, session, char, log):
        player: Player = session["player"]
        log.append("Você foi derrotado... Game Over.")
        await self._end_battle(battle_id, "derrota", session, char, player)
        return {
            "message": "Derrota.",
            "log": log,
            "result": "derrota",
            "character_health": 0,
        }

    async def _end_battle(self, battle_id, result, session, char, player, new_level=None):
        update_vals = {
            "health": max(player.health, 0),
            "is_alive": player.health > 0,
        }
        if new_level:
            update_vals["level"] = new_level

        await database.execute(
            characters.update().where(characters.c.id == char["id"]).values(**update_vals)
        )
        await database.execute(
            battles.update().where(battles.c.id == battle_id).values(result=result)
        )
        _active_battles.pop(battle_id, None)
