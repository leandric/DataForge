from fastapi import APIRouter, Depends, HTTPException, Response, Query
from typing import Annotated
from sqlmodel import Session, select, func
from uuid import UUID

from models.clientes_models import Cliente, ClientePost, ClienteResposta, ClientePut, ClientePatch, ConfirmaDelete
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

@router.put("/{uuid}", response_model=ClienteResposta,
    responses={
        404: {"description": "Cliente não encontrado"},
    },
)
def recadastra_cliente(uuid: UUID, cliente_update: ClientePut, session: SessionDep) -> ClienteResposta:
    cliente = session.exec(select(Cliente).where(Cliente.uuid == uuid)).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    dados = cliente_update.model_dump()  # dict com todos os campos do PUT
    for key, value in dados.items():
        setattr(cliente, key, value)

    session.add(cliente)
    session.commit()


    session.refresh(cliente)
    return ClienteResposta.model_validate(cliente)  # response_model faz a serialização


@router.patch(
    "/{uuid}",
    response_model=ClienteResposta,
    responses={
        404: {"description": "Cliente não encontrado"},
        400: {"description": "Nenhum dado recebido"},
    },
)
def atualiza_cliente(uuid: UUID, cliente_update: ClientePatch, session: SessionDep) -> ClienteResposta:
    update_data = cliente_update.model_dump(exclude_unset=True, exclude_none=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="Nenhum dado recebido")

    cliente = session.exec(select(Cliente).where(Cliente.uuid == uuid)).first()
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    for key, value in update_data.items():
        setattr(cliente, key, value)

    session.add(cliente)
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        # você pode manter genérico, já que não quer validar/inspecionar CPF
        raise HTTPException(status_code=400, detail="Erro ao atualizar cliente") from e

    session.refresh(cliente)
    return cliente

@router.delete("/{uuid}", response_model=ConfirmaDelete, responses={404:{'description':'Cliente não encontrado'}})
async def deleta_cliente(uuid:UUID, session:SessionDep) -> ConfirmaDelete:
    if cliente := session.exec(select(Cliente).where(Cliente.uuid == uuid)).first():
        nome = cliente.nome
        session.delete(cliente)
        session.commit()
        return ConfirmaDelete(mensagem=f"Cliente: {nome} deletado", uuid=uuid)
    raise HTTPException(status_code=404, detail="Cliente não encontrado")
