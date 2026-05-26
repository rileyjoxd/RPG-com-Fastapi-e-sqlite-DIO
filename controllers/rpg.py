from typing import Annotated
from fastapi import APIRouter, Depends, status

from schemas.rpg import CharacterCreateIn, UseItemIn, EquipItemIn
from security import login_required
from services.rpg import RPGService
from views.rpg import CharacterOut, BattleStartOut, BattleActionOut, BattleOut, ItemOut

router = APIRouter(prefix="/rpg", tags=["RPG"], dependencies=[Depends(login_required)])
service = RPGService()


# ── Personagem ────────────────────────────────────────────────────────

@router.post(
    "/character",
    response_model=CharacterOut,
    status_code=status.HTTP_201_CREATED,
    summary="Cria seu personagem",
)
async def create_character(
    data: CharacterCreateIn,
    current_user: Annotated[dict, Depends(login_required)],
):
    """Cria um personagem vinculado ao seu user_id. Só é permitido um por usuário."""
    return await service.create_character(current_user["user_id"], data.name)


@router.get(
    "/character",
    response_model=CharacterOut,
    summary="Status do personagem",
)
async def get_character(current_user: Annotated[dict, Depends(login_required)]):
    """Exibe HP, nível, arma e armadura equipados."""
    return await service.get_character(current_user["user_id"])


# ── Inventário ────────────────────────────────────────────────────────

@router.get(
    "/inventory",
    response_model=list[ItemOut],
    summary="Lista seu inventário",
)
async def get_inventory(current_user: Annotated[dict, Depends(login_required)]):
    return await service.get_inventory(current_user["user_id"])


@router.post(
    "/inventory/{item_id}/use",
    summary="Usa uma poção do inventário",
)
async def use_item(item_id: int, current_user: Annotated[dict, Depends(login_required)]):
    """Consome uma poção e recupera (ou perde) HP."""
    return await service.use_item(current_user["user_id"], item_id)


@router.post(
    "/inventory/{item_id}/equip",
    summary="Equipa arma ou armadura",
)
async def equip_item(item_id: int, current_user: Annotated[dict, Depends(login_required)]):
    """Equipa o item escolhido, substituindo o anterior do mesmo tipo."""
    return await service.equip_item(current_user["user_id"], item_id)


# ── Batalha ───────────────────────────────────────────────────────────

@router.post(
    "/battle/start",
    response_model=BattleStartOut,
    status_code=status.HTTP_201_CREATED,
    summary="Inicia uma batalha",
)
async def start_battle(current_user: Annotated[dict, Depends(login_required)]):
    """Gera um inimigo aleatório baseado no seu nível atual."""
    return await service.start_battle(current_user["user_id"])


@router.post(
    "/battle/{battle_id}/attack",
    response_model=BattleActionOut,
    summary="Ataca o inimigo",
)
async def attack(battle_id: int, current_user: Annotated[dict, Depends(login_required)]):
    """Executa uma rodada de ataque. O inimigo contra-ataca em seguida."""
    return await service.attack(current_user["user_id"], battle_id)


@router.post(
    "/battle/{battle_id}/flee",
    response_model=BattleActionOut,
    summary="Tenta fugir (40% de chance)",
)
async def flee(battle_id: int, current_user: Annotated[dict, Depends(login_required)]):
    """Se a fuga falhar, o inimigo ataca antes da próxima tentativa."""
    return await service.flee(current_user["user_id"], battle_id)


@router.get(
    "/battle/history",
    response_model=list[BattleOut],
    summary="Histórico de batalhas",
)
async def battle_history(current_user: Annotated[dict, Depends(login_required)]):
    """Lista todas as batalhas do seu personagem, da mais recente para a mais antiga."""
    return await service.get_battle_history(current_user["user_id"])
