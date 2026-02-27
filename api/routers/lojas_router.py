from fastapi import APIRouter, Depends, Response, Query, HTTPException, status
from typing import Annotated
from sqlmodel import Session, select, func


from models.lojas_models import Loja, LojaCreate, LojaRead, LojaUpdate
from database.database import get_session


router = APIRouter(prefix="/lojas", tags=["Lojas",])

SessionDep = Annotated[Session, Depends(get_session)]

@router.get("/", response_model=list[LojaRead])
async def listar(session:SessionDep, response:Response,page:int = Query(1, ge=1)) -> list[LojaRead]:
    page_size = 50

    total_items = session.exec(select(func.count()).select_from(Loja)).one()

    total_pages = (total_items + page_size -1) // page_size if total_items else 0

    if total_pages == 0:
        response.headers["X-Total-Pages"] = "0"
        response.headers["X-Total-Items"] = "0"
        return []
    
    page = min(page, total_pages)

    offset = (page -1) * page_size

    lojas = session.exec(
        select(Loja).limit(page_size).offset(offset)
    ).all()

    response.headers["X-Total-Pages"] = str(total_pages)
    response.headers["X-Total-Items"] = str(total_items)

    return [LojaRead.model_validate(l) for l in lojas]


@router.get("/{id_loja}", response_model=LojaRead, responses={404:{"description":"Loja não encontrada."}})
async def buscar_por_id(id_loja:int, session:SessionDep) -> LojaRead:
    loja = session.get(Loja, id_loja)

    if not loja:
        raise HTTPException(
            status_code=404,
            detail="Loja não encontrada."
        )
    
    return LojaRead.model_validate(loja)


@router.post("/", response_model=LojaRead, status_code=status.HTTP_201_CREATED)
async def cadastra_loja(loja_in:LojaCreate, session:SessionDep) -> LojaRead:

    loja = Loja.model_validate(loja_in)
    session.add(loja)
    session.commit()
    session.refresh(loja)

    return LojaRead.model_validate(loja)


@router.put("/{id_loja}", response_model=LojaRead,
            responses={404:{"description":"Loja não encontrada"}})
async def recadastra_loja(id_loja:int, loja_in:LojaCreate, session:SessionDep) -> LojaRead:
    loja = session.get(Loja, id_loja)

    if not loja:
        raise HTTPException(
            status_code=404,
            detail="Loja não encontrada"
        )

    loja_data = loja_in.model_dump()

    for key, value in loja_data.items():
        setattr(loja, key, value)

    session.add(loja)
    session.commit()
    session.refresh(loja)

    return LojaRead.model_validate(loja)


@router.patch(
    "/{id_loja}",
    response_model=LojaRead,
    responses={
        404: {"description": "Loja não encontrada"},
        400: {"description": "Nenhum dado recebido"},
    },
)
def atualizar_parcial(
    id_loja: int,
    loja_in: LojaUpdate,
    session: SessionDep,
) -> LojaRead:

    loja = session.get(Loja, id_loja)
    if not loja:
        raise HTTPException(status_code=404, detail="Loja não encontrada")

    update_data = loja_in.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado recebido")

    
    loja.sqlmodel_update(update_data)

    session.add(loja)
    session.commit()
    session.refresh(loja)

    return LojaRead.model_validate(loja)


@router.delete(
    "/{id_loja}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={404: {"description": "Loja não encontrada"}},
)
def deletar_produto(
    id_loja: int,
    session: SessionDep,
) -> None:

    loja = session.get(Loja, id_loja)

    if not loja:
        raise HTTPException(
            status_code=404,
            detail="Loja não encontrada"
        )

    session.delete(loja)
    session.commit()
