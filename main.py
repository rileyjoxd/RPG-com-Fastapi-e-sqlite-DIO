from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import database, engine, metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    from models import player, battle, inventory  # garante registro dos models
    await database.connect()
    metadata.create_all(engine)
    yield
    await database.disconnect()


app = FastAPI(
    title="RPG API",
    description="API assíncrona de RPG com batalhas, inventário e JWT.",
    version="1.0.0",
    lifespan=lifespan,
)

from controllers import auth, player, battle, inventory_ctrl

app.include_router(auth.router)
app.include_router(player.router)
app.include_router(battle.router)
app.include_router(inventory_ctrl.router)
