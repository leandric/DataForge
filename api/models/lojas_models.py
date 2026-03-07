from typing import List, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship


class LojaBase(SQLModel):
    nome_loja: str | None = Field(default=None, max_length=100)
    cidade: str | None = Field(default=None, max_length=100)
    estado: str = Field(max_length=2, nullable=False)
    data_abertura: datetime 


class Loja(LojaBase, table=True):
    id_loja: Optional[int] | None = Field(default=None, primary_key=True)

    vendas: List["Venda"] = Relationship(back_populates="loja")


class LojaCreate(LojaBase):
    ...


class LojaRead(LojaBase):
    ...


class LojaUpdate(SQLModel):
    nome_loja: str | None = Field(default=None, max_length=100)
    cidade: str | None = Field(default=None, max_length=100)
    estado: str | None = Field(default=None, max_length=2)
    data_abertura: datetime | None = None
