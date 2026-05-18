# AI_USAGE — Uso de Inteligência Artificial neste projeto

Este documento descreve, de forma honesta e auditável, **como
ferramentas de IA generativa foram usadas** no desenvolvimento do
**SRM Credit Engine**, o que foi delegado a elas, o que foi mantido
sob revisão humana e quais salvaguardas garantiram que o resultado
final fosse correto, seguro e defensável.

## Princípios

1. **Toda decisão arquitetural é humana.** ADRs são revisados antes
   de aceitos; nunca aceitos pela primeira sugestão do modelo.
2. **Todo código gerado é revisado.** Sem exceção. PR é o ponto de
   inspeção; CI é a rede de segurança.
3. **Toda alucinação detectada vira teste.** Se a IA inventou uma
   API ou comportamento, o teste fica para reprovar a alucinação
   futura.
4. **Documentar o uso é parte da qualidade.** Este arquivo é
   atualizado quando a forma de uso muda.

## Ferramentas utilizadas

| Ferramenta             | Papel principal                                        |
| ---------------------- | ------------------------------------------------------ |
| **GitHub Copilot Chat** | Geração de código (Python, TypeScript, SQL), explicação de erros, refatorações guiadas, escrita de testes. |
| **Modelos de linguagem (Claude / GPT-4 class)** | Brainstorming arquitetural, redação de ADRs e runbooks, revisão de PRs em modo "rubber duck". |
| **Copilot inline completion** | Boilerplate (DTOs, dataclasses, schemas Pydantic).  |

Não foram usados agentes autônomos que executam ações irreversíveis
sem revisão.

## O que foi delegado à IA

### Código

- **Boilerplate repetitivo** — schemas Pydantic, mapeamentos ORM,
  testes parametrizados de borda.
- **Conversão de pseudocódigo em código idiomático** — quando o
  algoritmo já estava decidido (ex.: juros compostos), o modelo
  produziu a implementação Python/TS limpa.
- **Adaptação de exemplos de documentação** — instrumentação OTel,
  configuração tenacity/purgatory, hooks pre-commit.
- **Tradução entre linguagens** — preservar a mesma semântica entre
  testes de pricing em Python e checagens equivalentes em TS.

### Documentação

- **Primeira versão de ADRs** com a estrutura
  contexto/opções/decisão/consequências; cada ADR foi reescrito após
  revisão humana.
- **Runbooks** — primeira versão dos cinco runbooks de crise; cada
  comando técnico (SQL, kubectl, psql) foi validado contra a
  documentação oficial antes de mergear.
- **Diagramas C4 em Mermaid** — geração da sintaxe; o conteúdo
  semântico (atores, containers, fronteiras) foi definido por
  humano.
- **Descrição dos PRs** seguindo template uniforme (Summary, Scope,
  Architectural notes, Testing, Risks, Out of Scope).

## O que NÃO foi delegado à IA

- **Modelagem de dados** — o ER foi desenhado manualmente; revisões
  da IA serviram apenas como sanity check.
- **Decisão de arquitetura** — escolhas Hexagonal vs camadas,
  Decimal-string vs float, retry+breaker+cache, single-DB vs schema
  por tenant: todas humanas; IA gerou apoio textual para os ADRs.
- **Avaliação de risco regulatório** — citação de CVM 175, ANBIMA,
  LGPD requer julgamento humano informado, não é fato gerado pelo
  modelo.
- **Aceite de PRs em `main`** — sempre revisão humana.
- **Conteúdo monetário ou estatístico final** — nenhum número
  apresentado em UI veio de cálculo "estimado" pelo modelo.

## Salvaguardas técnicas

1. **CI obrigatório** (lint, type check estrito, testes, build, build
   de imagem Docker) — bloqueia merge em caso de regressão.
2. **`mypy --strict`** no backend — alucinações de tipo são detectadas
   antes do humano olhar.
3. **`tsc --noEmit` + ESLint estrito** no frontend — mesma garantia.
4. **Cobertura ≥ 80%** com gate em CI — código gerado sem teste não
   passa.
5. **Pre-commit** local — primeiro filtro antes do push.
6. **Pull Requests descritivos** em `docs/pull-requests/` — cada PR
   tem um arquivo Markdown explicando intenção, escopo, riscos e o
   que ficou de fora.
7. **ADRs imutáveis** — nenhuma decisão muda silenciosamente; mudanças
   geram ADR novo que supersede o anterior.

## Procedimento de revisão de código gerado

Para cada bloco gerado por IA:

1. **Ler integralmente** antes de aceitar — nunca aceitar suggestion
   sem ler.
2. **Rodar testes** locais e em CI.
3. **Verificar a API** contra a documentação oficial — modelos podem
   alucinar parâmetros que não existem.
4. **Checar imports** — modelos às vezes referenciam pacotes que não
   estão no `pyproject.toml`/`package.json`.
5. **Validar comportamento de borda** — null, vazio, decimal preciso,
   timezone-aware datetime.
6. **Conferir consistência de estilo** com o resto do codebase
   (nomes, padrões de erro, formato de log).

## Alucinações comuns observadas e mitigações

| Alucinação                                            | Mitigação aplicada                                |
| ----------------------------------------------------- | ------------------------------------------------- |
| Pacotes inexistentes em sugestões de imports          | Verificação contra `pyproject.toml` / `package.json`; CI quebra. |
| APIs Pydantic v1 misturadas com v2                    | `mypy strict` + revisão manual.                   |
| `Decimal` operado com `float` ("isso compila")        | Convenção fixada em ADR-003; lint custom planejado. |
| Datas naïve (sem timezone)                            | Tipos `datetime` sempre `tzinfo=UTC` em domínio.  |
| Promessas de bibliotecas que "deveriam existir"       | Cross-check em PyPI / npm antes de adotar.        |
| SQL com `LIMIT` em update sem `RETURNING`             | Revisão humana de toda DDL/DML em migration.      |

## Métricas de uso (auto-reportadas)

| Categoria                          | Estimativa de assistência |
| ---------------------------------- | ------------------------- |
| Boilerplate (schemas, dataclasses) | Alta                      |
| Testes parametrizados              | Alta                      |
| Lógica de domínio (pricing core)   | Baixa (apoio incremental) |
| Decisões arquiteturais             | Apoio textual após decisão humana |
| Documentação narrativa             | Média (revisão pesada)    |
| Configuração de CI / Docker        | Alta na primeira versão; revisada |

Estes números são impressões qualitativas, não medidas precisas — não
há instrumentação automática medindo a proporção de código gerado por
IA versus escrito do zero.

## Conformidade e ética

- **Nenhum segredo, credencial ou dado real** foi compartilhado com
  ferramentas de IA. Exemplos usam dados sintéticos.
- **Código aberto utilizado pelos modelos** é tratado como referência;
  trechos copiados literalmente recebem atribuição quando o autor
  exige.
- **PII de cedente** nunca foi enviada para chat com IA — apenas
  shapes e tipos.
- **Decisões com impacto regulatório** (KYC, AML, retenção de dados)
  são tomadas por humano e registradas em ADR.

## Limitações conhecidas do uso de IA neste projeto

1. **Modelos podem desatualizar rápido** — sintaxe Pydantic v2,
   SQLAlchemy 2.0 async, Tailwind v4 e Vite 8 ainda têm exemplos
   antigos no treinamento. Revisão humana é a única salvaguarda.
2. **Contexto longo é limitado** — refatorações cross-file exigem
   prompts explícitos com caminhos e nomes; o modelo não enxerga o
   workspace inteiro.
3. **Falsa confiança em APIs externas** — quando o modelo "lembra" da
   AwesomeAPI, eu confiro contra a documentação atual.
4. **Repetição estilística** — sem instruções, o modelo tende a
   reintroduzir comentários verbosos; pre-commit/lint normaliza.

## Como reproduzir o desenvolvimento

Quem quiser reexecutar este projeto com IA pode seguir:

1. Use o plano em [docs/PLAN.md](PLAN.md) como roteiro de etapas.
2. Use os ADRs em [docs/adr/](adr/) como decisões pré-tomadas.
3. Para cada etapa, peça à IA **uma camada por vez** (domínio →
   infra → API → testes → docs).
4. **Não aceite a primeira saída** — revise, peça melhorias
   específicas, rode CI.
5. Atualize este `AI_USAGE.md` se a metodologia mudar.

---

**Última revisão:** acompanha o merge da Etapa 14 (README final +
AI_USAGE).
