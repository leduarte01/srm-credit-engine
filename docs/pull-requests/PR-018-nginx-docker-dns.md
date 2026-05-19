# PR #18 — Fix nginx Docker DNS resolver para EasyPanel Swarm

> GitHub PRs: leduarte01/srm-credit-engine#14 + #15

## Summary

Corrige resolução de DNS do nginx em ambiente Docker Swarm (EasyPanel).
O upstream `backend:8000` deixava de resolver no boot do container
porque o nginx default usa resolver do sistema operacional e cacheia
falhas. Adiciona um `resolver 127.0.0.11 valid=10s ipv6=off` explícito
ao bloco `http`, troca o upstream para o **nome completo do serviço
Swarm** (`tasks.srm_backend`) e adiciona rewrite explícito para o
prefixo `/api`. Resolve 502 intermitente após deploy.

## Scope

- `frontend/docker/nginx.conf` — `resolver` explícito + `set $upstream`
  via variável para forçar resolução por requisição + `rewrite ^/api/(.*)$ /$1 break;`.
- Sem mudança em código de aplicação.

## Quality gates

- `docker compose up` healthy localmente.
- Deploy no EasyPanel valida o roteamento.
