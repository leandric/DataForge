import time
from datetime import date, datetime, timezone
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

# ajuste o import do app conforme seu projeto
from main import app


def _cpf_11(i: int) -> str:
    """
    Gera um CPF pseudo-único de 11 dígitos (somente números).
    Não valida dígitos verificadores; serve para teste de carga/inserção.
    """
    return str(10_000_000_000 + i)  # garante 11 dígitos para i < 9_999_999_999


def _cliente_payload(i: int) -> dict:
    # Se seu schema aceita timezone no datetime, isso funciona bem.
    # Se preferir sem timezone: use datetime.utcnow().replace(tzinfo=None).isoformat()
    dt = datetime.now(timezone.utc).isoformat()

    return {
        "nome": f"Cliente {i}",
        "cpf": _cpf_11(i),
        "cidade": "São Paulo",
        "estado": "SP",
        "data_nascimento": date(1990, 1, 1).isoformat(),
        "data_criacao": dt,
    }


@pytest.mark.parametrize("n", [2000])  # troque para 5000, 10000, etc.
def test_cadastrar_milhares_de_clientes(n: int):
    client = TestClient(app)

    t0 = time.time()
    uuids: set[str] = set()

    for i in range(n):
        payload = _cliente_payload(i)
        r = client.post("/clientes", json=payload)

        # Se você implementou conflito de CPF, pode validar 201 sempre aqui.
        assert r.status_code == 201, f"Falhou no i={i}: {r.status_code} {r.text}"

        data = r.json()
        assert "uuid" in data
        # valida UUID de verdade
        UUID(data["uuid"])

        # garante que uuid não repetiu
        assert data["uuid"] not in uuids
        uuids.add(data["uuid"])

    elapsed = time.time() - t0
    # Não “quebra” por performance (isso varia muito), mas imprime um resumo útil.
    print(f"\nInseridos {n} clientes via API em {elapsed:.2f}s ({n/elapsed:.1f} req/s)")