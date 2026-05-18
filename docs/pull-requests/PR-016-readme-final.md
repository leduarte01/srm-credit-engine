# PR #16 — README final + AI_USAGE

## Summary
Reescreve o `README.md` da raiz como **ponto de entrada de
produção**: sumário navegável, stack com versões exatas, instruções
de início rápido via Docker, ciclo de desenvolvimento local
backend/frontend, estrutura do repositório anotada, lista de
endpoints REST, descrição do CI, mapa para a documentação
arquitetural (ADRs + C4 + high-scale + EDA + runbooks) e seção
explicando a postura do projeto sobre **uso de IA**. Substitui o
`frontend/README.md` (que ainda era o template default do Vite) por
uma versão alinhada ao stack real (React 19 + Tailwind v4 + TanStack
Query + axios + decimal.js) e às convenções não-negociáveis (dinheiro
em string, `ApiClientError` no boundary). Cria `docs/AI_USAGE.md`
documentando, de forma auditável, o que foi delegado à IA, o que NÃO
foi, salvaguardas técnicas (CI obrigatório, `mypy strict`, cobertura
≥ 80%, pre-commit, ADRs imutáveis), alucinações comuns observadas e
suas mitigações, e o procedimento de revisão. Nenhuma mudança de
código de produção — só documentação que torna o projeto
**explicável** para qualquer leitor novo (engenheiro, auditor,
gerente).

## Scope
- `README.md` — substitui o placeholder anterior por documentação
  completa: sumário, stack tabelada (linguagens, libs, versões),
  Início rápido (Docker), Desenvolvimento local (backend + frontend
  + pre-commit), Estrutura do repositório, tabela de endpoints
  principais, Qualidade e CI (três workflows + pre-commit + gate de
  cobertura), Arquitetura (mapa para `docs/architecture/`), Decisões
  registradas (tabela com os seis ADRs e seus status), Operação em
  crise (mapa para `runbooks/`), Versionamento (SemVer + GitHub
  Flow), Uso de IA (link para AI_USAGE) e Licença.
- `frontend/README.md` — apaga o template Vite default (instruções
  genéricas sobre `tseslint`, plugin swc, etc.) e substitui por:
  pré-requisitos reais (Node 22), scripts npm efetivamente usados,
  estrutura do `src/` por feature, regra de dinheiro-string, padrão
  `ApiClientError`, instruções de build Docker local.
- `docs/AI_USAGE.md` (novo) — documenta o uso de IA:
  - Princípios (decisão arquitetural é humana; código é revisado;
    alucinação detectada vira teste; documentar o uso é parte da
    qualidade).
  - Ferramentas usadas (Copilot Chat, modelos de linguagem para
    brainstorm/redação, inline completion).
  - O que foi delegado (boilerplate, conversão pseudocódigo→código,
    adaptação de exemplos OTel/tenacity, primeira versão de ADRs e
    runbooks, sintaxe Mermaid, descrição de PRs).
  - O que NÃO foi delegado (modelagem de dados, decisão
    arquitetural, avaliação regulatória, aceite de PR em `main`,
    cálculos monetários finais).
  - Salvaguardas técnicas (CI obrigatório, `mypy strict`, `tsc
    --noEmit` + ESLint, cobertura ≥ 80%, pre-commit, ADRs imutáveis,
    PR descritivos).
  - Procedimento de revisão de código gerado (ler antes de aceitar,
    rodar testes, verificar API contra doc oficial, checar imports,
    bordas, consistência estilística).
  - Tabela de alucinações comuns × mitigação aplicada (pacotes
    inexistentes, Pydantic v1/v2 misturado, Decimal × float, datas
    naïve, libs inexistentes, SQL inseguro).
  - Conformidade ética (nenhum segredo, nenhum PII real
    compartilhado; decisões regulatórias humanas).
  - Limitações conhecidas dos modelos (desatualização, contexto
    limitado, falsa confiança em APIs externas, ruído estilístico).
  - Receita para reproduzir o desenvolvimento usando o
    `docs/PLAN.md` como roteiro.
- `docs/COMMITS.md` — registra a Etapa 14.

## Architectural notes
- O README da raiz foi estruturado em **camadas progressivas de
  detalhe** — visitante casual lê sumário e Início rápido;
  contribuidor lê Desenvolvimento local + Qualidade; revisor
  arquitetural pula direto para Arquitetura + ADRs.
- A seção "Uso de IA" no README é deliberadamente **curta e
  honesta**; o detalhe vive em `docs/AI_USAGE.md` para não poluir o
  ponto de entrada.
- AI_USAGE foi escrito com **viés de auditoria**: lista o que NÃO foi
  feito por IA com a mesma ênfase do que foi feito, e enumera
  alucinações concretas que aconteceram + a mitigação aplicada. É um
  documento que sobrevive a perguntas adversariais.
- Todos os links internos usam **paths relativos** que funcionam
  tanto na renderização do GitHub quanto em editores Markdown
  offline.
- Nenhum link aponta para URL gerada/inventada — todos são internos
  ao repo ou para a documentação oficial das libs.

## Testing
- N/A — PR de documentação. Workflows existentes (`backend.yml`,
  `frontend.yml`, `docker.yml`) não são afetados.
- Pre-commit roda nos novos arquivos (hooks de hygiene: EOL,
  trailing-whitespace, large files).
- Validação visual: estrutura do README, tabelas, links internos e
  blocos de código renderizam corretamente no preview do GitHub.

## Risks & Mitigations
- **README desatualizar** — versões de libs e instruções podem ficar
  obsoletas. Mitigação: blocos de instalação são minimalistas
  (`uv sync`, `npm ci`) e seguem ferramentas idempotentes; versões
  específicas estão na tabela de Stack e podem ser atualizadas de
  uma vez.
- **AI_USAGE pode parecer "marketing"** — risco de soar como
  justificativa em vez de auditoria. Mitigação: o documento dedica
  espaço explícito a **alucinações observadas + limitações** e ao
  **que NÃO foi delegado**, com voz neutra.
- **Documentação dispersa** — README da raiz, READMEs por subpacote
  e `docs/`. Mitigação: README da raiz é o único hub; cada
  subdocumento é referenciado uma vez a partir dele e nunca
  duplica conteúdo.

## Out of Scope
- Tag de release `v1.0.0` e simulação de hotfix — ficam na Etapa 15
  (próximo PR).
- Tradução do README para outros idiomas.
- Geração automática de OpenAPI snapshot no repo (avaliar como
  follow-up se demanda surgir).
