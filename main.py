import os
import math
import random
from datetime import datetime, timedelta

import pandas as pd
from faker import Faker

fake = Faker("pt_BR")
random.seed(42)
Faker.seed(42)

BASE_DIR = "data_fake_bigdata"
os.makedirs(BASE_DIR, exist_ok=True)

# =========================
# 1) GERAR DIMENSÕES
# =========================

def gerar_dim_clientes(n_clientes=1_000_000):
    ids = range(1, n_clientes + 1)
    dados = {
        "id_cliente": ids,
        "nome": [fake.name() for _ in ids],
        "cpf": [fake.cpf() for _ in ids],
        "cidade": [fake.city() for _ in ids],
        "estado": [fake.estado_sigla() for _ in ids],
        "data_nascimento": [
            fake.date_between(start_date="-70y", end_date="-18y") for _ in ids
        ],
        "data_criacao": [
            fake.date_between(start_date="-5y", end_date="today") for _ in ids
        ],
    }
    df = pd.DataFrame(dados)
    caminho = os.path.join(BASE_DIR, "dim_clientes.parquet")
    df.to_parquet(caminho, index=False)
    print(f"dim_clientes -> {caminho} ({len(df):,} linhas)")


def gerar_dim_produtos(n_produtos=50_000):
    categorias = ["Eletrônicos", "Roupas", "Livros", "Mercado", "Brinquedos", "Esportes"]
    ids = range(1, n_produtos + 1)
    dados = {
        "id_produto": ids,
        "nome_produto": [f"Produto {i}" for i in ids],
        "categoria": [random.choice(categorias) for _ in ids],
        "preco_unitario": [round(random.uniform(10, 2000), 2) for _ in ids],
        "data_criacao": [
            fake.date_between(start_date="-5y", end_date="today") for _ in ids
        ],
    }
    df = pd.DataFrame(dados)
    caminho = os.path.join(BASE_DIR, "dim_produtos.parquet")
    df.to_parquet(caminho, index=False)
    print(f"dim_produtos -> {caminho} ({len(df):,} linhas)")


def gerar_dim_lojas(n_lojas=5_000):
    ids = range(1, n_lojas + 1)
    dados = {
        "id_loja": ids,
        "nome_loja": [f"Loja {i}" for i in ids],
        "cidade": [fake.city() for _ in ids],
        "estado": [fake.estado_sigla() for _ in ids],
        "data_abertura": [
            fake.date_between(start_date="-10y", end_date="today") for _ in ids
        ],
    }
    df = pd.DataFrame(dados)
    caminho = os.path.join(BASE_DIR, "dim_lojas.parquet")
    df.to_parquet(caminho, index=False)
    print(f"dim_lojas -> {caminho} ({len(df):,} linhas)")


# =========================
# 2) GERAR FATO VENDAS
# =========================

def gerar_fato_vendas(
    total_linhas=50_000_000,
    chunk_size=1_000_000,
):
    """
    Gera fato_vendas em vários arquivos parquet particionados por ano/mes.
    """
    # Carrega apenas os IDs das dimensões
    dim_clientes = pd.read_parquet(os.path.join(BASE_DIR, "dim_clientes.parquet"))[
        ["id_cliente"]
    ]
    dim_produtos = pd.read_parquet(os.path.join(BASE_DIR, "dim_produtos.parquet"))[
        ["id_produto", "preco_unitario"]
    ]
    dim_lojas = pd.read_parquet(os.path.join(BASE_DIR, "dim_lojas.parquet"))[
        ["id_loja"]
    ]

    cliente_ids = dim_clientes["id_cliente"].values
    produto_ids = dim_produtos["id_produto"].values
    preco_map = dict(
        zip(dim_produtos["id_produto"].values, dim_produtos["preco_unitario"].values)
    )
    loja_ids = dim_lojas["id_loja"].values

    fato_dir = os.path.join(BASE_DIR, "fato_vendas")
    os.makedirs(fato_dir, exist_ok=True)

    n_chunks = math.ceil(total_linhas / chunk_size)
    print(f"Gerando {total_linhas:,} linhas em {n_chunks} chunks…")

    data_inicio = datetime(2020, 1, 1)
    dias_range = (datetime(2025, 12, 31) - data_inicio).days

    linha_atual = 0
    for chunk_idx in range(n_chunks):
        linhas_nesse_chunk = min(chunk_size, total_linhas - linha_atual)

        # Gera dados sintéticos
        clientes_chunk = random.choices(cliente_ids, k=linhas_nesse_chunk)
        produtos_chunk = random.choices(produto_ids, k=linhas_nesse_chunk)
        lojas_chunk = random.choices(loja_ids, k=linhas_nesse_chunk)

        datas_venda = [
            data_inicio + timedelta(days=random.randint(0, dias_range))
            for _ in range(linhas_nesse_chunk)
        ]

        qtdes = [max(1, int(random.expovariate(1 / 3))) for _ in range(linhas_nesse_chunk)]

        valores_unitarios = [preco_map[p] for p in produtos_chunk]
        valores_totais = [
            round(q * vu * random.uniform(0.8, 1.1), 2)
            for q, vu in zip(qtdes, valores_unitarios)
        ]

        df_chunk = pd.DataFrame(
            {
                "id_venda": range(linha_atual + 1, linha_atual + 1 + linhas_nesse_chunk),
                "id_cliente": clientes_chunk,
                "id_produto": produtos_chunk,
                "id_loja": lojas_chunk,
                "data_venda": datas_venda,
                "quantidade": qtdes,
                "valor_unitario": valores_unitarios,
                "valor_total": valores_totais,
            }
        )

        # Particiona por ano/mes na gravação
        df_chunk["ano"] = df_chunk["data_venda"].dt.year
        df_chunk["mes"] = df_chunk["data_venda"].dt.month

        caminho_chunk = os.path.join(
            fato_dir, f"fato_vendas_chunk_{chunk_idx:04d}.parquet"
        )
        df_chunk.to_parquet(caminho_chunk, index=False)

        linha_atual += linhas_nesse_chunk
        print(
            f"Chunk {chunk_idx+1}/{n_chunks} -> {caminho_chunk} "
            f"({linhas_nesse_chunk:,} linhas, total gerado: {linha_atual:,})"
        )

    print("Concluído fato_vendas.")


if __name__ == "__main__":
    # Gera dimensões (uma vez só)
    gerar_dim_clientes(n_clientes=1_000_000)
    gerar_dim_produtos(n_produtos=50_000)
    gerar_dim_lojas(n_lojas=5_000)

    # Gera fato vendas gigante
    gerar_fato_vendas(
        total_linhas=50_000_000,  
        chunk_size=1_000_000,     
    )
