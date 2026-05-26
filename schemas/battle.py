from pydantic import BaseModel
from typing import Literal


class BattleAction(BaseModel):
    action: Literal["attack", "flee"]
