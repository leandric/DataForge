

# Gerador de Base Fake para Big Data / ETL

## 📌 Visão Geral

Este projeto fornece um **gerador de dados sintéticos em larga escala**, ideal para testes de:

* Pipelines ETL/ELT
* Big Data (Spark, Hadoop, Hive, Presto, DuckDB, etc.)
* Data Warehouses (Redshift, BigQuery, Snowflake)
* Modelagem dimensional (DW)
* Análises de performance e ingestão massiva

O script cria **dimensões realistas** e uma tabela fato com **dezenas ou centenas de milhões de linhas**, gravadas em arquivos **Parquet particionados** e gerados em *chunks* para evitar estouro de memória.

---

## 🚀 Funcionalidades

✔ Gera dimensões:

* `dim_clientes` (1 milhão de registros)
* `dim_produtos` (50 mil registros)
* `dim_lojas` (5 mil registros)

✔ Cria uma tabela:

* `fato_vendas` com até **bilhões de linhas**, geradas por chunks

✔ Produção em formato **Parquet**
✔ Dados simulados com:

* Distribuições mais realistas (quantidade, valores, datas)
* Relacionamentos consistentes entre dimensões e fato
* Uso do Faker para gerar informações brasileiras

✔ Organização em diretórios e particionamento por:

* Ano
* Mês

✔ Projeto ideal para testes de:

* Performance de leitura
* Carga de dados massiva
* Particionamento
* Processamento distribuído

---

## 🗂 Estrutura dos Dados Gerados

```
data_fake_bigdata/
│
├── dim_clientes.parquet
├── dim_produtos.parquet
├── dim_lojas.parquet
│
└── fato_vendas/
    ├── fato_vendas_chunk_0000.parquet
    ├── fato_vendas_chunk_0001.parquet
    └── ...
```

Cada chunk possui, por padrão, **1 milhão de linhas**, podendo ser ajustado.

---

## 📦 Instalação das Dependências

```bash
pip install faker pyarrow pandas
```

---

## 🧠 Como Funciona o Gerador

O script segue três etapas principais:

### **1) Criar dimensões**

Registra clientes, produtos e lojas com dados sintéticos.

### **2) Carregar apenas os IDs em memória**

Isso evita uso excessivo de RAM.

### **3) Gerar a tabela fato por chunks**

Cada chunk contém:

* FK de cliente, produto e loja
* Data da venda
* Quantidade (com distribuição exponencial)
* Valor unitário puxado da dim_produtos
* Valor total calculado

Cada chunk é salvo como Parquet, permitindo escalar para centenas de milhões de linhas.

---

## 🧪 Exemplos de Volumes Possíveis

| Tabela       | Linhas sugeridas | Observação             |
| ------------ | ---------------- | ---------------------- |
| dim_clientes | 1.000.000        | Pode aumentar para 10M |
| dim_produtos | 50.000           |                        |
| dim_lojas    | 5.000            |                        |
| fato_vendas  | 50.000.000+      | Ajustável até bilhões  |

Quantidade **não depende de RAM**, apenas de disco e tempo de execução.

---

## 🏗 Como Executar

### Execução padrão:

```bash
python gerar_base_fake.py
```

O script irá:

1. Criar as dimensões
2. Gerar 50 milhões de linhas para a tabela fato
3. Gravar tudo dentro da pasta `data_fake_bigdata/`

---

## ⚙ Configurações Importantes

No final do script:

```python
gerar_dim_clientes(n_clientes=1_000_000)
gerar_dim_produtos(n_produtos=50_000)
gerar_dim_lojas(n_lojas=5_000)

gerar_fato_vendas(
    total_linhas=50_000_000,
    chunk_size=1_000_000,
)
```

### Alterar volume total:

```python
total_linhas=500_000_000  # 500 milhões
```

### Alterar tamanho dos chunks:

```python
chunk_size=5_000_000
```

### Pequenos testes:

```python
total_linhas=1_000_000
chunk_size=200_000
```

---

## 📊 Exemplos de Uso em Ferramentas de Big Data

### **Spark**

```python
df = spark.read.parquet("data_fake_bigdata/fato_vendas")
df.groupBy("ano", "mes").sum("valor_total").show()
```

### **DuckDB**

```sql
SELECT ano, mes, SUM(valor_total)
FROM 'data_fake_bigdata/fato_vendas/*.parquet'
GROUP BY 1, 2;
```


## 📜 Licença

MIT License – Utilize e modifique livremente.