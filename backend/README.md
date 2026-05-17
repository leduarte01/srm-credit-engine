# Backend — SRM Credit Engine (Python)

Camada de aplicação (FastAPI) + domínio puro (sem framework) + infraestrutura (SQLAlchemy 2.0 async + asyncpg).

## Pré-requisitos
- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (gerenciador de pacotes recomendado)
- PostgreSQL 16 (ou rode via `docker-compose` na raiz do repo)

## Setup local

```powershell
# Instalar dependências
uv sync --dev

# Copiar variáveis de ambiente
Copy-Item .env.example .env

# Subir banco (na raiz do repo)
cd ..; docker compose up -d postgres; cd backend

# Aplicar migrations
uv run alembic upgrade head

# Rodar API em modo dev
uv run uvicorn srm_credit_engine.main:app --reload --host 0.0.0.0 --port 8000
```

## Comandos úteis

```powershell
uv run ruff check .              # lint
uv run ruff format .             # format
uv run mypy src                  # type check
uv run pytest                    # testes + coverage
uv run pytest -m "not integration"  # apenas unit
```

## Arquitetura (3 camadas)

```
src/srm_credit_engine/
├── api/              # Camada Aplicação (controllers/routers FastAPI)
├── domain/           # Camada Negócio (regras puras, sem framework)
└── infrastructure/   # Camada Persistência (DB, repositórios, gateways)
```

Consultas analíticas seguem o padrão **2 camadas** (`api → infrastructure/reports/`), bypassando a camada de domínio quando não há regra de negócio envolvida, em favor de SQL nativo otimizado.
