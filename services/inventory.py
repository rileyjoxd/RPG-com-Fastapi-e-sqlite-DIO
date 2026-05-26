from database import database
from databases.interfaces import Record
from fastapi import HTTPException, status
from models.inventory import inventory
from models.player import players


class InventoryService:

    async def get_inventory(self, player_id: int) -> list[Record]:
        return await database.fetch_all(
            inventory.select().where(inventory.c.player_id == player_id)
        )

    async def drop_item(self, player_id: int, item_id: int) -> dict:
        item = await database.fetch_one(
            inventory.select().where(inventory.c.id == item_id, inventory.c.player_id == player_id)
        )
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado.")

        # Se estava equipado, limpa o slot no player
        if item["equipped"]:
            if item["item_type"] == "weapon":
                await database.execute(
                    players.update().where(players.c.id == player_id).values(weapon_name=None)
                )
            elif item["item_type"] == "armor":
                await database.execute(
                    players.update().where(players.c.id == player_id).values(armor_name=None)
                )

        await database.execute(inventory.delete().where(inventory.c.id == item_id))
        return {"message": f"{item['item_name']} foi descartado."}

    async def equip_item(self, player_id: int, item_id: int) -> dict:
        item = await database.fetch_one(
            inventory.select().where(inventory.c.id == item_id, inventory.c.player_id == player_id)
        )
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado.")

        if item["item_type"] == "potion":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Poções não podem ser equipadas.")

        await database.execute(
            inventory.update()
            .where(inventory.c.player_id == player_id, inventory.c.item_type == item["item_type"])
            .values(equipped=False)
        )
        await database.execute(
            inventory.update().where(inventory.c.id == item_id).values(equipped=True)
        )

        if item["item_type"] == "weapon":
            await database.execute(
                players.update().where(players.c.id == player_id).values(weapon_name=item["item_name"])
            )
        elif item["item_type"] == "armor":
            await database.execute(
                players.update().where(players.c.id == player_id).values(armor_name=item["item_name"])
            )

        return {"message": f"{item['item_name']} equipado com sucesso!"}

    async def use_item(self, player_id: int, item_id: int) -> dict:
        item = await database.fetch_one(
            inventory.select().where(inventory.c.id == item_id, inventory.c.player_id == player_id)
        )
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item não encontrado.")

        if item["item_type"] != "potion":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Apenas poções podem ser usadas diretamente.")

        player = await database.fetch_one(players.select().where(players.c.id == player_id))
        new_health = player["health"] + item["heal"]

        await database.execute(
            players.update().where(players.c.id == player_id).values(health=new_health)
        )
        await database.execute(inventory.delete().where(inventory.c.id == item_id))

        heal = item["heal"]
        if heal >= 0:
            msg = f"Você usou {item['item_name']} e recuperou {heal} de HP. HP atual: {new_health}."
        else:
            msg = f"Você usou {item['item_name']} e perdeu {abs(heal)} de HP. HP atual: {new_health}. Não foi a melhor ideia."

        return {"message": msg, "new_health": new_health}
