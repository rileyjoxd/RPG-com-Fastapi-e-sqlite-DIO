from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import database, engine, metadata


@asynccontextmanager
async def lifespan(app: FastAPI):
    from models.rpg import characters, battles, inventory  # garante que as tabelas sejam registradas
    await database.connect()
    metadata.create_all(engine)
    yield
    await database.disconnect()


app = FastAPI(
    title="RPG API",
    description="API assíncrona de RPG com FastAPI + SQLite. Crie seu personagem, lute contra inimigos, colete itens e suba de nível!",
    version="1.0.0",
    lifespan=lifespan,
)

from controllers import auth, rpg  # noqa: E402

app.include_router(auth.router)
app.include_router(rpg.router)
