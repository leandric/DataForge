import asyncio
import time
from datetime import date, datetime, timezone
from uuid import UUID

import pytest
import httpx

from main import app


def _cpf_11(i: int) -> str:
    return str(10_000_000_000 + i)


def _cliente_payload(i: int) -> dict:
    return {
        "nome": f"Cliente {i}",
        "cpf": _cpf_11(i),
        "cidade": "São Paulo",
        "estado": "SP",
        "data_nascimento": date(1990, 1, 1).isoformat(),
        "data_criacao": datetime.now(timezone.utc).isoformat(),
    }


async def _worker(client: httpx.AsyncClient, sem: asyncio.Semaphore, i: int) -> str:
    async with sem:
        r = await client.post("/clientes", json=_cliente_payload(i))
        assert r.status_code in (200, 201), f"Falhou i={i}: {r.status_code} {r.text}"
        data = r.json()
        UUID(data["uuid"])
        return data["uuid"]


@pytest.mark.anyio
@pytest.mark.parametrize("n,concurrency", [(3000, 50)])
async def test_cadastrar_milhares_concorrente(n: int, concurrency: int):
    sem = asyncio.Semaphore(concurrency)
    t0 = time.time()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        tasks = [_worker(client, sem, i) for i in range(n)]
        uuids = await asyncio.gather(*tasks)

    assert len(uuids) == n
    assert len(set(uuids)) == n

    elapsed = time.time() - t0
    print(f"\nInseridos {n} clientes via API em {elapsed:.2f}s ({n/elapsed:.1f} req/s)")