from typing import Annotated
from fastapi import APIRouter, Depends
from security import login_required
from schemas.battle import BattleAction
from services.battle import BattleService
from views.battle import BattleStartOut, BattleActionOut, BattleOut

router = APIRouter(prefix="/battle", tags=["battle"], dependencies=[Depends(login_required)])
service = BattleService()


@router.post("/start", response_model=BattleStartOut, summary="Inicia uma batalha contra inimigo aleatório")
async def start_battle(current_user: Annotated[dict, Depends(login_required)]):
    return await service.start_battle(current_user["user_id"])


@router.post("/action", response_model=BattleActionOut, summary="Executa uma ação na batalha atual (attack ou flee)")
async def battle_action(data: BattleAction, current_user: Annotated[dict, Depends(login_required)]):
    return await service.battle_action(current_user["user_id"], data.action)


@router.get("/history", response_model=list[BattleOut], summary="Histórico de batalhas do personagem")
async def battle_history(current_user: Annotated[dict, Depends(login_required)]):
    return await service.get_history(current_user["user_id"])
