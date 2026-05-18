# Frontend — SRM Credit Engine

SPA em **React 19 + TypeScript + Vite 8 + Tailwind v4**. Consome a API
FastAPI em `/api/v1` (proxy `nginx` em produção, proxy do dev server
em desenvolvimento).

## Pré-requisitos
- Node 22+
- npm 10+

## Setup local

```bash
npm ci
cp .env.example .env
npm run dev          # http://localhost:5173
```

A variável `VITE_API_BASE_URL` controla a base da API. Em dev o
default é `/api/v1` (proxied pelo Vite para `http://localhost:8000`).
Em produção a build é servida por nginx, que faz proxy de
`/api/ → backend:8000/api/`.

## Scripts

```bash
npm run dev          # dev server + HMR
npm run build        # produção (saída em dist/)
npm run preview      # preview da build local
npm run lint         # eslint
npm run format       # prettier --write
npm run format:check # prettier --check (gate CI)
npm run test         # vitest run
npm run test:watch   # vitest watch
```

## Estrutura

```
frontend/
├── src/
│   ├── api/           # cliente axios + ApiClientError
│   ├── components/    # ui reutilizável
│   ├── features/      # módulos por contexto (assignors, receivables, pricing, ...)
│   ├── hooks/         # hooks compartilhados
│   ├── store/         # zustand stores
│   ├── routes/        # roteamento
│   └── main.tsx
├── docker/
│   └── nginx.conf     # produção: SPA fallback + /api/ proxy + /healthz
├── Dockerfile         # multi-stage (node:22-alpine → nginx:1.27-alpine)
├── vite.config.ts     # build
├── vitest.config.ts   # testes (separado para evitar conflito de tipos)
└── package.json
```

## Convenções importantes

- **Dinheiro é sempre `string`** no payload. Aritmética via
  `decimal.js`; apresentação via `Intl.NumberFormat`. Nunca
  `parseFloat` em campo monetário — ver
  [`docs/adr/ADR-003-decimal-money.md`](../docs/adr/ADR-003-decimal-money.md).
- **Erros da API** chegam por `ApiClientError` (`src/api/`), nunca
  por `axios.AxiosError` cru.
- **TanStack Query 5** para todo fetch remoto; chaves de cache
  estruturadas por feature.
- **Tailwind v4** com configuração inline em CSS — não há
  `tailwind.config.ts`.

## Docker (build local)

```bash
docker build -t srm-frontend .
docker run --rm -p 8080:80 srm-frontend
# http://localhost:8080
```

A imagem final é nginx servindo `/usr/share/nginx/html` com SPA
fallback e proxy `/api/`.
