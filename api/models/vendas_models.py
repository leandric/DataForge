from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field, Relationship


class VendaBase(SQLModel):
    # FKs (ajuste os nomes das tabelas conforme seu __tablename__ real)
    id_cliente: int = Field(foreign_key="cliente.id", index=True)
    id_produto: int = Field(foreign_key="produto.id_produto", index=True)
    id_loja: int = Field(foreign_key="loja.id_loja", index=True)

    data_venda: datetime = Field(index=True)

    quantidade: int
    valor_unitario: Decimal = Field(max_digits=10, decimal_places=2)
    valor_total: Decimal = Field(max_digits=12, decimal_places=2)

    ano: int = Field(index=True)
    mes: int = Field(index=True)


class Venda(VendaBase, table=True):
    __tablename__ = "vendas"  # troque para o nome real da tabela (ex: fato_vendas)

    id_venda: int | None = Field(default=None, primary_key=True)

    # Relationships (strings por causa de forward refs)
    cliente: "Cliente" = Relationship(back_populates="vendas")
    produto: "Produto" = Relationship(back_populates="vendas")
    loja: "Loja" = Relationship(back_populates="vendas")


class VendaCreate(VendaBase):
    pass


class VendaRead(VendaBase):
    id_venda: int

    # extras solicitados
    nome_cliente: str | None = None
    nome_produto: str | None = None


class VendaUpdate(SQLModel):
    # PATCH (tudo opcional)
    id_cliente: int | None = None
    id_produto: int | None = None
    id_loja: int | None = None

    data_venda: datetime | None = None

    quantidade: int | None = None
    valor_unitario: Decimal | None = None
    valor_total: Decimal | None = None

    ano: int | None = None
    mes: int | None = None