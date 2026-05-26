from pydantic import BaseModel


class EquipItem(BaseModel):
    item_id: int


class UseItem(BaseModel):
    item_id: int
