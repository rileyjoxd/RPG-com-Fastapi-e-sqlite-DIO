from typing import Annotated
from fastapi import APIRouter, Depends
from security import login_required
from services.player import PlayerService
from views.player import PlayerOut

router = APIRouter(prefix="/players", tags=["players"])
service = PlayerService()


@router.get("/", response_model=list[PlayerOut], summary="Lista todos os personagens (ranking por nível)")
async def list_players():
    return await service.list_all()


@router.get("/me", response_model=PlayerOut, summary="Retorna o personagem autenticado")
async def get_me(current_user: Annotated[dict, Depends(login_required)]):
    return await service.get_by_id(current_user["user_id"])


@router.post("/revive", response_model=PlayerOut, summary="Ressuscita o personagem morto com HP base")
async def revive(current_user: Annotated[dict, Depends(login_required)]):
    return await service.revive(current_user["user_id"])


@router.get("/{player_id}", response_model=PlayerOut, summary="Retorna um personagem pelo ID")
async def get_player(player_id: int):
    return await service.get_by_id(player_id)
