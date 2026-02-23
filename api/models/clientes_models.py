from __future__ import annotations

from datetime import date, datetime
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class ClienteBase(SQLModel):
    nome: str = Field(max_length=255, index=True, nullable=False)

    cpf: str = Field(
        max_length=11,
        index=True,
        nullable=False,
        unique=True,
        description="CPF somente números (11 dígitos).",
    )

    cidade: str = Field(max_length=100, index=True, nullable=False)
    estado: str = Field(max_length=2, index=True, nullable=False)

    data_nascimento: date = Field(nullable=False)

    # Agora: vem do cliente, então não use default_factory
    data_criacao: datetime = Field(nullable=False)


class Cliente(ClienteBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

    uuid: UUID = Field(
        default_factory=uuid4,
        index=True,
        unique=True,
        nullable=False,
    )


class ClienteResposta(ClienteBase):
    uuid: UUID


# POST/PUT: incluem data_criacao
class ClientePost(ClienteBase):
    ...


class ClientePut(ClienteBase):
    ...


# PATCH: manter tipos corretos (datetime/date)
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
