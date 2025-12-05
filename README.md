

# 🔥 DataForge — Gerador de Dados Sintéticos para Projetos de Big Data e ETL

O **DataForge** é um gerador de dados sintéticos em larga escala projetado para facilitar testes, validações e experimentos em ambientes de **Big Data**, **Data Engineering** e **Data Warehousing**.

A proposta do projeto é fornecer uma forma simples, flexível e realista de criar bases massivas — desde alguns milhões até bilhões de registros — simulando cenários comuns do mundo corporativo, como vendas, clientes, produtos e lojas.


---


O DataForge simula uma arquitetura de **Data Warehouse** completa, gerando tanto **tabelas dimensão** quanto **tabelas fato**.
A geração acontece em **chunks**, o que permite criar volumes extremamente grandes sem consumir muita RAM.

Entre os principais objetivos do projeto estão:

* Criar uma base sintética **realista e consistente**
* Permitir escalabilidade ajustável (milhões → bilhões)
* Testar pipelines de ingestão com grande volume e variedade
* Oferecer um dataset seguro (sem dados reais)
* Facilitar estudos de modelagem dimensional e performance

---
## Documentação

* [Docuementação do código](docs/base_generator.md)
* [Documentação da base de dados](docs/doc_base_de_dados.md)
