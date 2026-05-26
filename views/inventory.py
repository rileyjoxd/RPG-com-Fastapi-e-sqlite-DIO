from pydantic import BaseModel


class ItemOut(BaseModel):
    id: int
    item_name: str
    item_type: str
    rarity: str
    damage_bonus: int | None = None
    crit_rate: int | None = None
    defense_bonus: int | None = None
    heal: int | None = None
    equipped: bool
