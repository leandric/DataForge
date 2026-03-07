from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class VendaBase(SQLModel):
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
    __tablename__ = "vendas"

    id_venda: Optional[int] | None = Field(default=None, primary_key=True)

    cliente: Optional["Cliente"] = Relationship(back_populates="vendas")
    produto: Optional["Produto"] = Relationship(back_populates="vendas")
    loja: Optional["Loja"] = Relationship(back_populates="vendas")


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