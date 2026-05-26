from typing import Annotated
from fastapi import APIRouter, Depends
from security import login_required
from schemas.inventory import EquipItem, UseItem
from services.inventory import InventoryService
from views.inventory import ItemOut

router = APIRouter(prefix="/inventory", tags=["inventory"], dependencies=[Depends(login_required)])
service = InventoryService()


@router.get("/", response_model=list[ItemOut], summary="Lista o inventário do personagem")
async def get_inventory(current_user: Annotated[dict, Depends(login_required)]):
    return await service.get_inventory(current_user["user_id"])


@router.post("/equip", summary="Equipa uma arma ou armadura")
async def equip_item(data: EquipItem, current_user: Annotated[dict, Depends(login_required)]):
    return await service.equip_item(current_user["user_id"], data.item_id)


@router.post("/use", summary="Usa uma poção do inventário")
async def use_item(data: UseItem, current_user: Annotated[dict, Depends(login_required)]):
    return await service.use_item(current_user["user_id"], data.item_id)


@router.delete("/{item_id}", summary="Descarta um item do inventário")
async def drop_item(item_id: int, current_user: Annotated[dict, Depends(login_required)]):
    return await service.drop_item(current_user["user_id"], item_id)
