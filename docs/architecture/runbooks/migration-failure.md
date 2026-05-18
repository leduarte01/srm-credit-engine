# Runbook — Migração de banco falhou

**Severidade:** P1 (deploy bloqueado; rollback necessário).

## Contexto

Migrações são executadas pelo `entrypoint.sh` do container backend
antes do `uvicorn`, comandadas por `alembic upgrade head` quando
`RUN_MIGRATIONS=true`.

Falha aqui mantém o container em **CrashLoopBackOff**, o serviço não
sobe.

## Detecção

- Pods do backend em `CrashLoopBackOff`.
- Logs com `alembic.runtime.migration: ERROR`.
- Métrica `kube_pod_status_ready{condition="false"}` para os pods novos.
- Versão antiga continua servindo se rolling update — saúde do serviço
  parcial.

## Diagnóstico (≤ 5 min)

1. `kubectl logs <pod> --previous` (ou equivalente) — capturar a
   exceção exata.
2. Identificar a revision alvo:
   ```bash
   alembic current   # no DB
   alembic heads     # no código
   ```
3. Classificar a falha:
   - **A) Conflito de schema** (coluna já existe / não existe).
   - **B) Constraint não satisfeita por dados existentes**
     (NOT NULL em coluna nova; UNIQUE com duplicatas).
   - **C) Deadlock / lock timeout** em migração de tabela grande.
   - **D) Erro de sintaxe / lógica na própria revision**.

## Mitigação

### A) Conflito de schema

Geralmente DDL idempotente ausente. Não rode `alembic downgrade` em
produção sem revisão.

1. Capturar estado atual: `\d+ <tabela>` no `psql`.
2. Decidir: editar a migration (com PR + revisão) ou criar nova
   migration corretiva.
3. **Nunca** edite o arquivo de revision já aplicado em outro
   ambiente.

### B) Constraint violada por dados

Padrão recomendado para coluna NOT NULL:
1. Adicionar coluna NULL.
2. Backfill em batches.
3. Em migration seguinte, aplicar `SET NOT NULL`.

**Mitigação imediata:** se a migration falhou no passo 3:
- Identificar linhas problemáticas (`WHERE col IS NULL`).
- Corrigir dados via PR de data-fix (em script versionado).
- Re-aplicar a migration.

### C) Deadlock / lock timeout

Migrações em tabelas grandes precisam de `SET lock_timeout = '5s'` e
`SET statement_timeout = '30s'`. Se travou:
1. Identificar locks bloqueadores em `pg_stat_activity`.
2. Cancelar a migration: `pg_cancel_backend(pid)`.
3. Reescrever a migration para usar `CREATE INDEX CONCURRENTLY` /
   `ALTER TABLE ... ADD COLUMN` separado de `ADD CONSTRAINT`.

### D) Erro na revision

1. **Rollback do deploy** mantém o serviço estável na versão anterior.
2. Corrigir a revision em uma branch nova; abrir PR; mergear; redeploy.
3. **Nunca** rode `alembic downgrade` em produção a menos que a
   migration tenha sido escrita explicitamente reversível e testada.

## Recuperação

1. Verificar `alembic current` no DB == `alembic heads` no código.
2. Pods sobem; `/health/ready` retorna 200.
3. Validar smoke tests críticos.

## Verificação pós-incidente

- [ ] Backup do DB anterior à migration está disponível.
- [ ] Nenhum dado foi perdido (conferir contagens antes/depois).
- [ ] PR de fix passou CI completo.
- [ ] Pós-mortem aberto.

## Prevenção

- **Toda migration roda em CI** num PostgreSQL real antes de merge.
- **Smoke test de rollback** quando a migration é reversível.
- **Migrations grandes em duas fases** (DDL + backfill + DDL final).
- **Lock timeout sempre setado** no início da migration.
- **`RUN_MIGRATIONS=true` apenas em job dedicado** em ambientes grandes
  (não no entrypoint do app).
