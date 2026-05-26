from pydantic import BaseModel
from datetime import datetime


class LoginOut(BaseModel):
    access_token: str


class ItemOut(BaseModel):
    id: int
    item_name: str
    item_type: str
    rarity: str
    value: int
    extra: int
    equipped: bool


class CharacterOut(BaseModel):
    id: int
    user_id: int
    name: str
    health: int
    damage: int
    defense: int
    critical: int
    level: int
    weapon_name: str | None
    armor_name: str | None
    is_alive: bool


class BattleStartOut(BaseModel):
    message: str
    battle_id: int
    enemy_name: str
    enemy_health: int
    character_health: int


class BattleActionOut(BaseModel):
    message: str
    log: list[str]
    battle_id: int | None = None
    enemy_health: int | None = None
    character_health: int | None = None
    result: str | None = None          # vitoria / derrota / fuga / em_andamento
    drops: list[str] | None = None
    level_up: bool = False


class BattleOut(BaseModel):
    id: int
    enemy_name: str
    enemy_health_start: int
    result: str | None
    rounds: int
    created_at: datetime
