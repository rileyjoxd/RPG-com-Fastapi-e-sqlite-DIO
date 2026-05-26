from pydantic import BaseModel


class PlayerOut(BaseModel):
    id: int
    name: str
    health: int
    damage: int
    critical: int
    defense: int
    level: int
    coins: int
    victories: int
    weapon_name: str | None = None
    armor_name: str | None = None
