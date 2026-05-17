# PR #3 — Backend Bootstrap (Python + FastAPI)

**Branch:** `feat/backend-bootstrap` → `main`
**Tipo:** feat / chore

## O que foi feito
- `backend/pyproject.toml`: configuração completa do projeto Python (deps de runtime + dev), Ruff (lint+format), Mypy strict, Pytest com cobertura mínima de 80%
- `backend/.python-version` (3.12), `backend/.env.example`, `backend/README.md`
- Estrutura de 3 camadas: `src/srm_credit_engine/{api,domain,infrastructure}`
- `config.py` — Pydantic Settings com cache (12-factor)
- `main.py` — FastAPI app com healthcheck `/health`
- Domínio:
  - `value_objects/Money` — Decimal-only, banker's rounding, imutável
  - `exceptions.py` — hierarquia `DomainError` com `code` e `http_status` para tradução por handler global
- Testes: `tests/unit/test_money.py` (8 cenários incluindo rejeição de `float`)

## Decisões
- **Decimal obrigatório**: `Money` rejeita `float` no construtor (segurança financeira)
- **`Money` frozen + slots**: imutabilidade real + economia de memória
- **Mypy strict**: compensa tipagem dinâmica do Python
- **Ruff substitui** flake8 + isort + black + bandit (S rules)
- **Settings cacheado** com `@lru_cache`: leitura única do `.env`

## Checklist
- [x] Arquitetura em 3 camadas (`api` / `domain` / `infrastructure`)
- [x] Tipagem forte (mypy --strict)
- [x] Linter de segurança (Ruff S rules)
- [x] Healthcheck para Docker/K8s
