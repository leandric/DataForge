from typing import List, Optional
from typing import List
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship


class ProdutoBase(SQLModel):
    nome_produto: str | None = Field(default=None, max_length=255)
    categoria: str = Field(max_length=100)
    preco_unitario: Decimal = Field(max_digits=10, decimal_places=2)
    data_criacao: datetime = Field(default_factory=datetime.utcnow)


class Produto(ProdutoBase, table=True):
    id_produto: Optional[int] | None = Field(default=None, primary_key=True)

    vendas: List["Venda"] = Relationship(back_populates="produto")


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoRead(ProdutoBase):
    id_produto: int


class ProdutoUpdate(SQLModel):
    nome_produto: str | None = None
    categoria: str | None = None
    preco_unitario: Decimal | None = None