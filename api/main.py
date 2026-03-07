from contextlib import asynccontextmanager
from fastapi import FastAPI
import models  # noqa: F401

from database.database import criar_db_tabelas
from routers import cliente_router
from routers import produtos_router
from routers import lojas_router
from routers import venda_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    criar_db_tabelas()
    yield
    # Shutdown (se quiser, pode fechar conexões, etc.)


app = FastAPI(
    title="API DataForge",
    lifespan=lifespan,
)

app.include_router(cliente_router.router)
app.include_router(produtos_router.router)
app.include_router(lojas_router.router)
app.include_router(venda_router.router)
