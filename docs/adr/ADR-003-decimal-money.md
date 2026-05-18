# ADR-003 — Representação de valores monetários como `Decimal` serializado em string

| Status | Data       | Decisor    |
| ------ | ---------- | ---------- |
| Aceito | 2026-04-12 | Engenharia |

## Contexto

O **SRM Credit Engine** opera sobre valores financeiros (face value de
recebíveis, juros, taxas administrativas, conversões cambiais). Erros de
representação de ponto flutuante geram inconsistência contábil e
auditável — `0.1 + 0.2 != 0.3` é inaceitável em domínio bancário.

A representação precisa sobreviver a:

- **Cálculo backend** (juros simples e compostos, multiplicação por
  taxas, divisão por dias úteis).
- **Persistência em PostgreSQL** (decimais com precisão e escala
  controladas).
- **Boundary HTTP** (JSON não tem tipo decimal nativo — apenas number
  IEEE 754 e string).
- **Frontend React/TypeScript** (`number` em JS é IEEE 754 double).

## Opções avaliadas

### 1. `float` / `number` no JSON

- 👍 Simples; serialização nativa.
- 👎 Perda silenciosa de precisão em conversões e arredondamentos.
- 👎 `JSON.parse("123.45")` em JS gera double com erro de
  representação.

### 2. `Decimal` no backend + `number` no JSON

- 👍 Cálculo backend preciso.
- 👎 Mantém o problema no boundary — o frontend recebe float.
- 👎 Pydantic v2 default serializa `Decimal` como número, expondo a falha.

### 3. **`Decimal` backend + string no JSON + biblioteca decimal no frontend** ✅

- 👍 Precisão preservada em toda a borda — JSON transporta string,
  nunca número.
- 👍 Cálculo backend feito com `decimal.Decimal` e contexto explícito.
- 👍 Frontend usa `decimal.js` (ou similar) para qualquer aritmética em
  decimais; apresentação usa `Intl.NumberFormat`.
- 👎 Validação Pydantic precisa ser explícita (`Decimal` via
  `model_serializer` ou tipo customizado).
- 👎 Operações JS triviais (`a + b`) não funcionam — requer wrapper.

## Decisão

Adotar **`Decimal` no backend, serializado como string no JSON**, com as
seguintes regras:

1. **Domínio:** `Money` é um Value Object encapsulando `Decimal` + ISO
   currency code. Operações aritméticas vivem no VO.
2. **Pydantic schemas:** campos monetários usam `Decimal` com
   `model_config = ConfigDict(json_encoders=...)` e
   `field_serializer` para emitir string.
3. **PostgreSQL:** colunas `NUMERIC(20, 8)` (8 casas decimais cobrem
   câmbio cripto-grau; 20 dígitos cobrem trilhões de unidades).
4. **Frontend:** todos os campos monetários chegam como `string`. Aritmética
   feita via `decimal.js`. Apresentação via `Intl.NumberFormat` com
   `currency`.
5. **Contexto Decimal:** `getcontext().prec = 28`; rounding default
   `ROUND_HALF_EVEN` (banker's rounding — padrão IEEE 754 e regulatório).

## Consequências

### Positivas

- Auditoria contábil consegue reconciliar centavos sem ambiguidade.
- Conversão de moeda preserva precisão entre Decimal × Decimal → Decimal.
- Testes de pricing comparam strings — diff legível em PR.

### Negativas (e mitigação)

- Frontend não pode usar `Number(value)` sem perder precisão — mitigado
  por convenção documentada e linter custom (`no-restricted-syntax` para
  `parseFloat` em campos monetários).
- Pydantic exige boilerplate de serialização — encapsulado em
  `MoneyField` reutilizável.

## Referências

- IEEE 754; Python `decimal` module.
- `decimal.js` — David Bau.
- BCB Resolução nº 4.918 (precisão contábil).
