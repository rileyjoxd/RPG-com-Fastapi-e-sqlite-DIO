from pydantic import BaseModel
from datetime import datetime


class BattleOut(BaseModel):
    id: int
    player_id: int
    enemy_name: str
    result: str
    damage_dealt: int
    damage_taken: int
    loot: str | None = None
    created_at: datetime | None = None


class BattleStartOut(BaseModel):
    message: str
    enemy_name: str
    enemy_health: int
    enemy_damage: int
    enemy_defense: int
    player_health: int


class BattleActionOut(BaseModel):
    message: str
    player_health: int
    enemy_health: int
    result: str | None = None  # victory, defeat, fled, ongoing, status para monitoramento da batalha, são auto explicativos.
    loot: list[str] | None = None
    level_up: bool = False
    new_level: int | None = None
