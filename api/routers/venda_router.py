from fastapi import APIRouter, Depends, Response, Query, HTTPException, status
from typing import Annotated
from sqlmodel import Session, select, func
from sqlalchemy.orm import selectinload

from models.vendas_models import Venda, VendaCreate, VendaRead, VendaUpdate
from database.database import get_session

router = APIRouter(prefix="/venda", tags=["Venda"])

SessionDep = Annotated[Session, Depends(get_session)]


def _to_read(venda: Venda) -> VendaRead:
    """Converte Venda (ORM) -> VendaRead incluindo nome_cliente e nome_produto."""
    out = VendaRead.model_validate(venda)
    out.nome_cliente = getattr(getattr(venda, "cliente", None), "nome", None)
    out.nome_produto = getattr(getattr(venda, "produto", None), "nome_produto", None)
    return out


@router.get("/", response_model=list[VendaRead])
def listar_vendas(
    session: SessionDep,
    response: Response,
    page: int = Query(1, ge=1),
) -> list[VendaRead]:
    PAGE_SIZE = 50

    total_items = session.exec(select(func.count()).select_from(Venda)).one()  # type: ignore
    total_pages = (total_items + PAGE_SIZE - 1) // PAGE_SIZE

    if page > total_pages and total_pages > 0:
        page = total_pages

    offset = (page - 1) * PAGE_SIZE

    stmt = (
        select(Venda)
        .options(selectinload(Venda.cliente), selectinload(Venda.produto))
        .offset(offset)
        .limit(PAGE_SIZE)
        .order_by(Venda.id_venda.desc())
    )
    vendas = session.exec(stmt).all()

    response.headers["X-Total-Items"] = str(total_items)
    response.headers["X-Total-Pages"] = str(total_pages)
    response.headers["X-Page"] = str(page)
    response.headers["X-Page-Size"] = str(PAGE_SIZE)

    return [_to_read(v) for v in vendas]


@router.get("/{id_venda}", response_model=VendaRead, responses={404: {"description": "Venda não encontrada"}})
def obter_venda(id_venda: int, session: SessionDep) -> VendaRead:
    stmt = (
        select(Venda)
        .where(Venda.id_venda == id_venda)
        .options(selectinload(Venda.cliente), selectinload(Venda.produto))
    )
    venda = session.exec(stmt).first()
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")
    return _to_read(venda)


@router.post("/", response_model=VendaRead, status_code=status.HTTP_201_CREATED)
def criar_venda(venda_in: VendaCreate, session: SessionDep) -> VendaRead:
    venda = Venda.model_validate(venda_in)

    # Opcional: se quiser garantir consistência (não confiar no cliente)
    # venda.valor_total = venda.quantidade * venda.valor_unitario

    session.add(venda)
    session.commit()
    session.refresh(venda)

    # Recarrega com relationships para preencher nomes
    stmt = (
        select(Venda)
        .where(Venda.id_venda == venda.id_venda)
        .options(selectinload(Venda.cliente), selectinload(Venda.produto))
    )
    venda_db = session.exec(stmt).one()
    return _to_read(venda_db)


@router.put("/{id_venda}", response_model=VendaRead, responses={404: {"description": "Venda não encontrada"}})
def substituir_venda(id_venda: int, venda_in: VendaCreate, session: SessionDep) -> VendaRead:
    venda = session.exec(select(Venda).where(Venda.id_venda == id_venda)).first()
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")

    data = venda_in.model_dump()
    for k, v in data.items():
        setattr(venda, k, v)

    session.add(venda)
    session.commit()
    session.refresh(venda)

    stmt = (
        select(Venda)
        .where(Venda.id_venda == id_venda)
        .options(selectinload(Venda.cliente), selectinload(Venda.produto))
    )
    venda_db = session.exec(stmt).one()
    return _to_read(venda_db)


@router.patch("/{id_venda}", response_model=VendaRead, responses={404: {"description": "Venda não encontrada"}, 400: {"description": "Nenhum dado recebido"}})
def atualizar_venda(id_venda: int, venda_upd: VendaUpdate, session: SessionDep) -> VendaRead:
    update_data = venda_upd.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado recebido")

    venda = session.exec(select(Venda).where(Venda.id_venda == id_venda)).first()
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")

    for k, v in update_data.items():
        setattr(venda, k, v)

    # Opcional: manter consistência se quantidade/valor_unitario mudarem
    # if "quantidade" in update_data or "valor_unitario" in update_data:
    #     venda.valor_total = venda.quantidade * venda.valor_unitario

    session.add(venda)
    session.commit()
    session.refresh(venda)

    stmt = (
        select(Venda)
        .where(Venda.id_venda == id_venda)
        .options(selectinload(Venda.cliente), selectinload(Venda.produto))
    )
    venda_db = session.exec(stmt).one()
    return _to_read(venda_db)


@router.delete("/{id_venda}", status_code=status.HTTP_204_NO_CONTENT, responses={404: {"description": "Venda não encontrada"}})
def deletar_venda(id_venda: int, session: SessionDep) -> None:
    venda = session.exec(select(Venda).where(Venda.id_venda == id_venda)).first()
    if not venda:
        raise HTTPException(status_code=404, detail="Venda não encontrada")

    session.delete(venda)
    session.commit()
    return None