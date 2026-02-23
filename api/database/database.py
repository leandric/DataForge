from sqlmodel import create_engine, Session, SQLModel
from dotenv import load_dotenv
import os

# Garanta que os models sejam importados para registrar no metadata
from models.clientes_models import Cliente  # noqa: F401

load_dotenv()

DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "meu_banco")

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?charset=utf8mb4"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,            # True só em dev
    pool_pre_ping=True,   # evita conexão morta
    pool_recycle=1800,    # recicla conexões (MySQL costuma derrubar idle)
    pool_size=5,
    max_overflow=10,
)


def criar_db_tabelas() -> None:
    SQLModel.metadata.create_all(engine)


def get_session():
    session = Session(engine)
    try:
        yield session
        # Em geral, commit/rollback ficam no endpoint/service.
        # Se você preferir commitar aqui automaticamente, dá pra fazer,
        # mas normalmente é melhor controlar na camada de negócio.
    finally:
        session.close()
