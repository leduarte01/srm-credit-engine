# Arquitetura — visão geral

Este diretório descreve a arquitetura do **SRM Credit Engine** em
quatro eixos complementares:

| Documento                                  | Pergunta que responde                              |
| ------------------------------------------ | -------------------------------------------------- |
| [C4 — Contexto](c4-context.md)             | Quem usa o sistema e com o que ele conversa?       |
| [C4 — Containers](c4-containers.md)        | Quais peças tecnológicas compõem o sistema?       |
| [C4 — Componentes](c4-components.md)       | Como o backend é organizado internamente?         |
| [High-scale](high-scale.md)                | Como esta arquitetura sobrevive a 10×/100× carga? |
| [EDA / outbox](eda.md)                     | Como integrar via eventos sem perder consistência? |
| [Runbooks](runbooks/)                      | O que fazer quando algo quebrar?                   |

As **decisões arquiteturais imutáveis** que sustentam estes documentos
estão em [`../adr/`](../adr/README.md).
