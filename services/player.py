from database import database
from databases.interfaces import Record
from fastapi import HTTPException, status
from models.player import players
from schemas.player import PlayerCreate


class PlayerService:
    async def create(self, data: PlayerCreate) -> int:
        existing = await database.fetch_one(
            players.select().where(players.c.name == data.name)
        )
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Nome já existe.")
        return await database.execute(players.insert().values(
            name=data.name,
            health=100,
            damage=10,
            critical=5,
            defense=0,
            level=1,
            coins=0,
            victories=0,
        ))

    async def get_by_id(self, player_id: int) -> Record:
        player = await database.fetch_one(players.select().where(players.c.id == player_id))
        if not player:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Personagem não encontrado.")
        return player

    async def revive(self, player_id: int) -> Record:
        player = await self.get_by_id(player_id)
        if player["health"] > 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seu personagem não está morto.")
        await database.execute(
            players.update().where(players.c.id == player_id).values(health=100)
        )
        return await self.get_by_id(player_id)

    async def list_all(self) -> list[Record]:
        return await database.fetch_all(players.select().order_by(players.c.level.desc()))
