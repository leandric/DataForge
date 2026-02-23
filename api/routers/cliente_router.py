from fastapi import APIRouter, Depends, HTTPException, Response, Query
from typing import Annotated
from sqlmodel import Session, select, func
from uuid import UUID

from models.clientes_models import Cliente, ClientePost, ClienteResposta
from database.database import get_session  # ajuste o caminho conforme seu projeto

router = APIRouter(prefix="/clientes", tags=["Clientes"])

SessionDep = Annotated[Session, Depends(get_session)]


@router.get("/", response_model=list[ClienteResposta])
def listar(session: SessionDep, response:Response, page:int=Query(1,  ge=1)) -> list[ClienteResposta]:
    PAGE_SIZE = 50
    total_items = session.exec(select(func.count()).select_from(Cliente)).one() # type:ignore
    total_pages = (total_items +PAGE_SIZE -1) //PAGE_SIZE

    if page > total_pages and total_pages > 0:
        page = total_pages

    offset = (page - 1) * PAGE_SIZE
    query = (
        select(Cliente)
        .limit(PAGE_SIZE)
        .offset(offset)
    )

    clientes = session.exec(query).all()

    response.headers['X-Total-Pages'] = str(total_pages)
    response.headers['X-Total-Items'] = str(total_items)

    return [ClienteResposta.model_validate(cliente) for cliente in clientes]

@router.get("/{uuid}", response_model=ClienteResposta, responses={404:{'description':'Cliente não encontrado'}})
async def get_cliente(uuid: UUID, session: SessionDep) -> ClienteResposta:
    if cliente := session.exec(select(Cliente).where(Cliente.uuid == uuid)).first():
        return ClienteResposta.model_validate(cliente)
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

@router.post("/", response_model=ClienteResposta, status_code=201)
def criar(payload: ClientePost, session: SessionDep):
    cliente = Cliente(**payload.model_dump())
    session.add(cliente)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        # Você pode refinar: se for erro de UNIQUE no cpf, retornar 409
        raise HTTPException(status_code=400, detail="Erro ao criar cliente.") from e

    session.refresh(cliente)
    return cliente