from datetime import date, datetime
from uuid import UUID, uuid4
from typing import List, Optional
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Relationship

class ClienteBase(SQLModel):
    nome: str = Field(max_length=255, index=True, nullable=False)
    cpf: str = Field(max_length=11, index=True, nullable=False, unique=True)
    cidade: str = Field(max_length=100, index=True, nullable=False)
    estado: str = Field(max_length=2, index=True, nullable=False)
    data_nascimento: date = Field(nullable=False)
    data_criacao: datetime = Field(nullable=False)

class Cliente(ClienteBase, table=True):
    __tablename__ = "cliente"

    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: UUID = Field(default_factory=uuid4, index=True, unique=True, nullable=False)

    vendas: List["Venda"] = Relationship(back_populates="cliente")

class ClienteResposta(ClienteBase):
    uuid: UUID

class ClientePost(ClienteBase):
    ...

class ClientePut(ClienteBase):
    ...

class ClientePatch(SQLModel):
    nome: str | None = None
    cpf: str | None = None
    cidade: str | None = None
    estado: str | None = None
    data_nascimento: date | None = None
    data_criacao: datetime | None = None

class ConfirmaDelete(BaseModel):
    mensagem: str
    uuid: UUID