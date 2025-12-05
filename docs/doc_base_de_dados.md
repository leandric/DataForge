
# 📘 Documentação da Base de Dados — Data Warehouse Fake para Big Data / ETL

Esta documentação descreve o modelo de dados gerado pelo script, seus relacionamentos, chaves primárias/estrangeiras e exemplos de consultas SQL com *joins* e análises típicas de DW.

---

# 🧩 1. Visão Geral do Modelo

A base segue um **modelo dimensional**, contendo:

* **Tabelas dimensão**

  * `dim_clientes`
  * `dim_produtos`
  * `dim_lojas`

* **Tabela fato**

  * `fato_vendas`

A tabela fato registra eventos de vendas, referenciando as dimensões via chaves substitutas.

---

# 🗂 2. Diagrama Conceitual

```
 dim_clientes         dim_produtos          dim_lojas
   (1:N)                 (1:N)                (1:N)
        \                   |                     /
         \                  |                    /
          \                 |                   /
               ---- fato_vendas ----
```

---

# 🔑 3. Dicionário das Tabelas

## 3.1. `dim_clientes`

| Coluna          | Tipo   | Descrição                      |
| --------------- | ------ | ------------------------------ |
| id_cliente (PK) | INT    | Identificador único do cliente |
| nome            | STRING | Nome completo                  |
| cpf             | STRING | CPF gerado pelo Faker          |
| cidade          | STRING | Cidade de residência           |
| estado          | STRING | UF                             |
| data_nascimento | DATE   | Data de nascimento             |
| data_criacao    | DATE   | Data de criação do cadastro    |

---

## 3.2. `dim_produtos`

| Coluna          | Tipo   | Descrição                             |
| --------------- | ------ | ------------------------------------- |
| id_produto (PK) | INT    | Identificador único do produto        |
| nome_produto    | STRING | Nome do produto                       |
| categoria       | STRING | Categoria (eletrônicos, roupas, etc.) |
| preco_unitario  | FLOAT  | Preço base                            |
| data_criacao    | DATE   | Data de inclusão no catálogo          |

---

## 3.3. `dim_lojas`

| Coluna        | Tipo   | Descrição                   |
| ------------- | ------ | --------------------------- |
| id_loja (PK)  | INT    | Identificador único da loja |
| nome_loja     | STRING | Nome comercial              |
| cidade        | STRING | Cidade                      |
| estado        | STRING | UF                          |
| data_abertura | DATE   | Data de abertura da loja    |

---

## 3.4. `fato_vendas`

| Coluna          | Tipo   | Descrição                                      |
| --------------- | ------ | ---------------------------------------------- |
| id_venda (PK)   | BIGINT | Identificador único da venda                   |
| id_cliente (FK) | INT    | Referência a `dim_clientes`                    |
| id_produto (FK) | INT    | Referência a `dim_produtos`                    |
| id_loja (FK)    | INT    | Referência a `dim_lojas`                       |
| data_venda      | DATE   | Data da transação                              |
| quantidade      | INT    | Quantidade de itens vendidos                   |
| valor_unitario  | FLOAT  | Valor original do produto                      |
| valor_total     | FLOAT  | Valor da venda (qtd × preço × fator aleatório) |
| ano             | INT    | Particionamento por ano                        |
| mes             | INT    | Particionamento por mês                        |

---

# 🔗 4. Relacionamentos

| Tabela Fato → Dimensão                           | Relacionamento | Tipo |
| ------------------------------------------------ | -------------- | ---- |
| fato_vendas.id_cliente → dim_clientes.id_cliente | N:1            | FK   |
| fato_vendas.id_produto → dim_produtos.id_produto | N:1            | FK   |
| fato_vendas.id_loja → dim_lojas.id_loja          | N:1            | FK   |

Cada linha de venda sempre possui:

* um cliente
* um produto
* uma loja

---

# 🧪 5. Exemplos de Consultas SQL

A seguir estão querys típicas que você executaria em Redshift, BigQuery, Spark SQL, Presto ou DuckDB.

---

## 5.1. **Total de vendas por ano**

```sql
SELECT 
    ano,
    SUM(valor_total) AS faturamento
FROM fato_vendas
GROUP BY ano
ORDER BY ano;
```

---

## 5.2. **JOIN com clientes — vendas por estado**

```sql
SELECT 
    c.estado,
    SUM(f.valor_total) AS faturamento
FROM fato_vendas f
JOIN dim_clientes c 
    ON f.id_cliente = c.id_cliente
GROUP BY c.estado
ORDER BY faturamento DESC;
```

---

## 5.3. **JOIN com produtos — faturamento por categoria**

```sql
SELECT 
    p.categoria,
    COUNT(*) AS total_vendas,
    SUM(f.valor_total) AS faturamento
FROM fato_vendas f
JOIN dim_produtos p 
    ON f.id_produto = p.id_produto
GROUP BY p.categoria;
```

---

## 5.4. **Análise por loja + mês**

```sql
SELECT 
    l.nome_loja,
    f.ano,
    f.mes,
    SUM(f.valor_total) AS faturamento_mensal
FROM fato_vendas f
JOIN dim_lojas l 
    ON f.id_loja = l.id_loja
GROUP BY l.nome_loja, f.ano, f.mes
ORDER BY faturamento_mensal DESC;
```

---

## 5.5. **Ticket médio por cliente**

```sql
SELECT 
    c.id_cliente,
    c.nome,
    SUM(f.valor_total) / COUNT(*) AS ticket_medio
FROM fato_vendas f
JOIN dim_clientes c ON f.id_cliente = c.id_cliente
GROUP BY c.id_cliente, c.nome
ORDER BY ticket_medio DESC
LIMIT 20;
```

---

## 5.6. **Produtos mais vendidos por quantidade**

```sql
SELECT 
    p.nome_produto,
    SUM(f.quantidade) AS qtd_total
FROM fato_vendas f
JOIN dim_produtos p ON f.id_produto = p.id_produto
GROUP BY p.nome_produto
ORDER BY qtd_total DESC
LIMIT 20;
```

---

## 5.7. **Distribuição de vendas por data — exemplo de agregação diária**

```sql
SELECT 
    data_venda,
    SUM(valor_total) AS faturamento
FROM fato_vendas
GROUP BY data_venda
ORDER BY data_venda;
```

---

## 5.8. **Exemplo de análise multijoin**

Combining all dimensions:

```sql
SELECT 
    f.id_venda,
    c.nome AS cliente,
    p.nome_produto,
    l.nome_loja,
    f.data_venda,
    f.quantidade,
    f.valor_total
FROM fato_vendas f
JOIN dim_clientes c ON f.id_cliente = c.id_cliente
JOIN dim_produtos p ON f.id_produto = p.id_produto
JOIN dim_lojas l ON f.id_loja = l.id_loja
WHERE f.ano = 2024 AND f.mes = 5
ORDER BY f.data_venda;
```

---

# 📊 6. Possíveis Derivações e Análises

### Exemplos de análises reais que você pode treinar:

* Análise por cohort de clientes
* Curva ABC de produtos
* Previsão de vendas por dia/mês
* Avaliação de sazonalidade
* Análise por canal/região/UF
* Enriquecimento com lookup incremental

Também permite testar:

* Particionamento eficiente
* Z-Order / sort keys (Spark/Redshift)
* Ingestão massiva com COPY (Redshift)
* Organização bronze → silver → gold
