from fastapi import APIRouter, Depends, Response, Query, HTTPException, status
from typing import Annotated
from sqlmodel import Session, select, func

from models.produtos_model import Produto, ProdutoRead, ProdutoCreate, ProdutoUpdate
from database.database import get_session

router = APIRouter(prefix="/produtos", tags=["Produtos"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/", response_model=list[ProdutoRead])
def listar(
    session: SessionDep,
    response: Response,
    page: int = Query(1, ge=1),
) -> list[ProdutoRead]:
    page_size = 50

    # COUNT(*) correto
    total_items = session.exec(
        select(func.count()).select_from(Produto)
    ).one()

    # total_pages deve ser 0 quando total_items == 0
    total_pages = (total_items + page_size - 1) // page_size if total_items else 0

    # se não há itens, retorna lista vazia
    if total_pages == 0:
        response.headers["X-Total-Pages"] = "0"
        response.headers["X-Total-Items"] = "0"
        return []

    # clamp da página
    page = min(page, total_pages)

    offset = (page - 1) * page_size

    produtos = session.exec(
        select(Produto).limit(page_size).offset(offset)
    ).all()

    response.headers["X-Total-Pages"] = str(total_pages)
    response.headers["X-Total-Items"] = str(total_items)

    # Não sobrescreva o nome da classe Produto com variável
    return [ProdutoRead.model_validate(p) for p in produtos]


@router.get(
    "/{id_produto}",
    response_model=ProdutoRead,
    responses={404: {"description": "Produto não encontrado"}},
)
def buscar_por_id(
    id_produto: int,
    session: SessionDep,
) -> ProdutoRead:

    produto = session.get(Produto, id_produto)

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    return ProdutoRead.model_validate(produto)


@router.post(
    "/",
    response_model=ProdutoRead,
    status_code=status.HTTP_201_CREATED,
)
def criar_produto(
    produto_in: ProdutoCreate,
    session: SessionDep,
) -> ProdutoRead:

    produto = Produto.model_validate(produto_in)

    session.add(produto)
    session.commit()
    session.refresh(produto)

    return ProdutoRead.model_validate(produto)


@router.put(
    "/{id_produto}",
    response_model=ProdutoRead,
    responses={404: {"description": "Produto não encontrado"}},
)
def atualizar_produto(
    id_produto: int,
    produto_in: ProdutoCreate,
    session: SessionDep,
) -> ProdutoRead:

    produto = session.get(Produto, id_produto)

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    # Atualização completa (substitui todos os campos editáveis)
    produto_data = produto_in.model_dump()

    for key, value in produto_data.items():
        setattr(produto, key, value)

    session.add(produto)
    session.commit()
    session.refresh(produto)

    return ProdutoRead.model_validate(produto)


@router.patch(
    "/{id_produto}",
    response_model=ProdutoRead,
    responses={
        404: {"description": "Produto não encontrado"},
        400: {"description": "Nenhum dado recebido"},
    },
)
def atualizar_parcial(
    id_produto: int,
    produto_in: ProdutoUpdate,
    session: SessionDep,
) -> ProdutoRead:

    produto = session.get(Produto, id_produto)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    update_data = produto_in.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado recebido")

    
    produto.sqlmodel_update(update_data)

    session.add(produto)
    session.commit()
    session.refresh(produto)

    return ProdutoRead.model_validate(produto)


@router.delete(
    "/{id_produto}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Produto não encontrado"}},
)
def deletar_produto(
    id_produto: int,
    session: SessionDep,
) -> None:

    produto = session.get(Produto, id_produto)

    if not produto:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado"
        )

    session.delete(produto)
    session.commit()