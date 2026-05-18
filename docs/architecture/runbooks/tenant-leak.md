# Runbook — Suspeita de vazamento cross-tenant

**Severidade:** P0 (risco regulatório imediato; ver
[ADR-006](../../adr/ADR-006-multi-tenancy.md)).

## Detecção

| Sinal                                                       | Origem                       |
| ----------------------------------------------------------- | ---------------------------- |
| Usuário reporta ver dado de outro fundo                     | Suporte / canal de incidente |
| Auditoria interna detecta linha sem `tenant_id` correto     | SQL ad-hoc                   |
| Teste de RLS falha em CI                                    | `pytest`                     |
| Log estruturado com `tenant_id` ≠ `auth.tenant_id`          | structlog query              |

## Tratamento — primeiras ações (≤ 15 min)

1. **Isolar o tenant afetado.** Desabilitar logins:
   ```sql
   UPDATE tenant SET status='locked', locked_at=now()
   WHERE id IN (:reporting_tenant, :leaked_tenant);
   ```
2. **Congelar deploys** até o root cause estar identificado.
3. **Abrir canal de incidente** (P0); incluir compliance e
   jurídico.
4. **Preservar evidências**:
   - Snapshot da tabela suspeita.
   - Logs das últimas 24h filtrados por `tenant_id` envolvido.
   - Traces OTel correspondentes.

## Diagnóstico

### Linha 1 — RLS está ativa?

```sql
SELECT tablename, rowsecurity, forcerowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = true;
```

Todas as tabelas de domínio devem ter `rowsecurity=true` e
`forcerowsecurity=true`.

### Linha 2 — Policy correta?

```sql
SELECT policyname, tablename, qual
FROM pg_policies WHERE schemaname='public';
```

`qual` deve referenciar `tenant_id = current_setting('app.tenant_id')::uuid`.

### Linha 3 — App está setando o tenant em cada checkout?

Inspecionar o middleware:
- Existe `SET app.tenant_id = ...` no início de cada transação?
- Quem é o owner do papel usado pela aplicação? RLS ignora `SUPERUSER`!

### Linha 4 — Existe query sem filtro de tenant?

Buscar repositórios sem `tenant_id` no `WHERE`:
```bash
grep -rn "select\|update\|delete" backend/src/srm_credit_engine/infrastructure/
```

Toda query SQL de domínio deve filtrar por `tenant_id`.

### Linha 5 — Cache?

Algum cache (memória, Redis) sem prefixo por tenant?

## Mitigação imediata

| Causa identificada                              | Ação                                              |
| ----------------------------------------------- | ------------------------------------------------- |
| Query sem `tenant_id` em repositório            | Hotfix imediato; revert do deploy se possível.    |
| RLS desativada por erro de migration            | Reativar via psql:`ALTER TABLE ... FORCE ROW LEVEL SECURITY;` |
| Conta de aplicação com `SUPERUSER`              | Revogar `SUPERUSER`; rotacionar credencial.       |
| Cache sem prefixo de tenant                     | Flush imediato do cache.                          |
| Token JWT com `tenant_id` incorreto             | Invalidar todas as sessões; rotacionar chave.     |

## Recuperação

1. Confirmar fix por meio de **teste automatizado de isolamento**
   adicionado ao mesmo PR.
2. Restaurar acesso dos tenants afetados.
3. Enviar comunicação formal:
   - Tenant impactado: qual dado foi exposto, por quanto tempo, a quem.
   - Compliance: relatório completo.

## Verificação pós-incidente

- [ ] Teste de RLS rodando em CI a cada PR.
- [ ] Auditoria SQL — nenhuma linha sem `tenant_id` plausível.
- [ ] Credenciais rotacionadas se houver suspeita.
- [ ] Notificação regulatória avaliada com jurídico (LGPD / CVM).
- [ ] Pós-mortem **público para tenants afetados** (resumo executivo).

## Prevenção

- **CI roda suite dedicada de RLS** com dois tenants e tenta acesso
  cruzado.
- **Linter custom** (`grep` pre-commit) reprovando `session.execute(...)`
  com query crua sem `tenant_id`.
- **Repositório base** que injeta `tenant_id` automaticamente —
  desenvolvedor não escreve `WHERE tenant_id`.
- **Conta de aplicação sem `SUPERUSER` em nenhum ambiente.**
- **Auditoria periódica** (quinzenal) de policies de RLS.
