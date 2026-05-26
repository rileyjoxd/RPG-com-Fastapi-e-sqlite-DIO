from fastapi import APIRouter, HTTPException, status
from database import database
from models.player import players
from schemas.player import PlayerCreate, PlayerLogin
from security import sign_jwt
from views.player import PlayerOut
from services.player import PlayerService

router = APIRouter(prefix="/auth", tags=["auth"])
service = PlayerService()


@router.post("/register", response_model=PlayerOut, status_code=status.HTTP_201_CREATED,
             summary="Cria um novo personagem")
async def register(data: PlayerCreate):
    """Cria um novo personagem com nome único."""
    player_id = await service.create(data)
    return await service.get_by_id(player_id)


@router.post("/login", summary="Gera token JWT para o personagem")
async def login(data: PlayerLogin):
    """Recebe o ID do personagem e retorna o token de acesso."""
    await service.get_by_id(data.player_id)  # valida se existe
    return sign_jwt(data.player_id)
