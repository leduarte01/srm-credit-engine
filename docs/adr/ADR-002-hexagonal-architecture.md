# ADR-002 — Arquitetura Hexagonal (Ports & Adapters) no backend

| Status | Data       | Decisor    |
| ------ | ---------- | ---------- |
| Aceito | 2026-04-12 | Engenharia |

## Contexto

O backend do **SRM Credit Engine** modela um domínio financeiro com regras
sensíveis (precificação de recebíveis com juros simples e compostos,
liquidações, conversão de moeda) que precisam ser:

- **Testáveis sem infraestrutura** — regra de negócio não pode depender
  de PostgreSQL, HTTP nem de um provedor externo de câmbio.
- **Auditáveis** — a lógica de pricing tem que ser inspecionável como uma
  função pura `Receivable → PricedReceivable`, sem efeito colateral
  escondido.
- **Substituíveis** — o provedor de câmbio (AwesomeAPI hoje) ou o
  mecanismo de persistência (SQLAlchemy hoje) podem mudar sem reescrever
  a camada de domínio.
- **Compostos com resiliência transversal** — retries, circuit breakers e
  cache de câmbio são preocupações de adaptador, não de domínio.

## Opções avaliadas

### 1. Arquitetura em camadas tradicional (`controllers → services → repositories`)

Três camadas onde a camada de serviço importa diretamente repositórios
SQLAlchemy.

- 👍 Simples, familiar.
- 👎 Acopla regra de negócio ao ORM: testar pricing exige sessão
  SQLAlchemy mockada.
- 👎 Tornar um adaptador externo (câmbio) substituível requer abstração
  manual ad-hoc.
- 👎 Cresce mal em projetos com múltiplos adaptadores externos.

### 2. Clean Architecture (Uncle Bob) com casos de uso

Quatro camadas concêntricas com `UseCase` explícito por operação.

- 👍 Forte separação por intenção.
- 👎 Volume de classes e DTOs duplicados (`Request`/`Response`/`Entity`)
  desproporcional ao tamanho atual do domínio.
- 👎 KISS: criar `PriceReceivableUseCase` para cada endpoint repetiria
  estrutura de serviço sem ganho prático.

### 3. **Arquitetura Hexagonal (Ports & Adapters)** ✅

Domínio puro no centro; **portas** (interfaces `Protocol`) definidas pelo
domínio; **adaptadores** de entrada (FastAPI) e de saída
(SQLAlchemy, HTTP de câmbio) implementam as portas.

- 👍 Domínio testável com `unittest` puro — entidades como `Receivable`
  são `dataclass`-like sem dependência externa.
- 👍 Portas (`CurrencyConverter`, `ReceivableRepository`) são `Protocol`s
  Python — _structural typing_ permite múltiplas implementações sem
  herança.
- 👍 Resiliência (retries, circuit breaker, cache em DB) entra como
  **adaptador decorator** (`ResilientCurrencyConverter`) sem poluir o
  domínio.
- 👍 Composição feita em `api/v1/deps.py` (Composition Root) — um único
  lugar onde adaptadores reais são plugados nas portas.
- 👎 Mais arquivos que abordagem em camadas — aceito em troca de
  isolamento e testabilidade.

## Decisão

Adotar **Arquitetura Hexagonal** com a seguinte estrutura:

```
src/srm_credit_engine/
├── domain/                    # núcleo puro, sem imports de infra
│   ├── entities/              # Assignor, Receivable, Settlement, ...
│   ├── value_objects/         # Money (Decimal string), Cnpj, DateRange
│   ├── ports/                 # Protocols: ReceivableRepository, CurrencyConverter
│   ├── services/              # Lógica de negócio orquestrada
│   ├── pricing/               # Calculadora de juros simples/compostos
│   ├── analytics/             # Sumarizações de carteira
│   └── exceptions.py          # Erros de domínio (DomainError, NotFound, ...)
│
├── api/v1/                    # adaptador de entrada (FastAPI)
│   ├── routers/               # endpoints REST, traduzem HTTP ↔ domínio
│   ├── schemas/               # Pydantic v2 (somente boundary HTTP)
│   ├── deps.py                # Composition Root (DI)
│   └── errors.py              # mapeia DomainError → HTTP
│
├── infrastructure/            # adaptadores de saída
│   ├── database.py            # AsyncSession factory
│   ├── models.py              # SQLAlchemy ORM (separado das entidades!)
│   ├── mappers.py             # Mapper ORM ↔ entidade de domínio
│   ├── repositories.py        # implementa ports/*.Repository
│   └── database_currency_converter.py  # cache em DB
│
├── resilience/                # decorators externos
│   ├── retries.py             # tenacity wrappers
│   ├── circuit_breaker.py     # purgatory wrappers
│   └── resilient_converter.py # Decorator de CurrencyConverter
│
├── observability/             # OTel + Prometheus + structlog
└── main.py                    # bootstrap FastAPI
```

**Regra de dependência:** `domain/` **não importa** de nenhum outro
pacote do projeto. Tudo que entra no domínio entra por meio de uma porta
(Protocol).

## Consequências

### Positivas

- Testes de pricing rodam em milissegundos sem `pytest-asyncio` nem fixtures
  de banco.
- Adição de um segundo provedor de câmbio (fallback) é uma nova classe que
  implementa `CurrencyConverter` — zero mudança no domínio.
- Auditoria regulatória pode inspecionar `domain/pricing/` isoladamente,
  sem ruído de infraestrutura.
- A camada `resilience/` é composta no Composition Root como
  `ResilientCurrencyConverter(DatabaseCurrencyConverter(...))` — o domínio
  enxerga apenas `CurrencyConverter`.

### Negativas (e mitigação)

- Mapeamento ORM ↔ Entidade exige `mappers.py` — mitigado mantendo
  entidades e modelos com nomes alinhados e cobrindo `mappers` com testes
  de ida-e-volta.
- Mais arquivos para navegar — mitigado pela estrutura plana por contexto
  (não há sub-sub-sub-pacotes).

## Referências

- Alistair Cockburn, _Hexagonal Architecture_ (2005).
- Vaughn Vernon, _Implementing Domain-Driven Design_ (2013).
