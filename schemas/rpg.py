from pydantic import BaseModel


class LoginIn(BaseModel):
    user_id: int


class CharacterCreateIn(BaseModel):
    name: str


class AttackIn(BaseModel):
    """Jogador ataca o inimigo atual."""
    pass


class UseItemIn(BaseModel):
    item_id: int


class EquipItemIn(BaseModel):
    item_id: int


class FleeIn(BaseModel):
    """Tenta fugir da batalha."""
    pass
