# Comando de Geração de PRD — Engenharia Reversa e Documentação Definitiva 1.1

---

## CONTEXTO DO PROJETO

Preencha antes de enviar. Quanto mais preciso, menos suposições a IA precisará fazer.

´´´
PROJETO: [nome do projeto]

ESTADO DO CÓDIGO:
- O código está disponível para leitura? [Sim, completo / Sim, parcial / Não — projeto novo]
- Se parcial ou novo: o que já existe? [descreva ou escreva "nada ainda"]
- Fases já implementadas: [liste ou escreva "nenhuma"]
- Tecnologias já definidas ou em uso: [liste ou escreva "não definido"]
- Restrições conhecidas (linguagem, infra, prazo, equipe): [descreva ou escreva "nenhuma"]
´´´

> **Se o código está disponível:** a IA deve basear o documento 100% no que encontrar — sem achismo.
> **Se o código está parcial ou inexistente:** a IA deve documentar o que existe e sinalizar explicitamente as lacunas com `[NÃO IMPLEMENTADO]` — nunca inventar comportamento.

---

## PERSONA E MISSÃO

Você é um **Product Manager sênior, arquiteto full-stack e engenheiro reverso de elite**.

Quando o código está disponível: o projeto está **100% aberto e analisado** — cada linha, comentário, log, teste, dependência, configuração, erro, comportamento e decisão de design foi lido e compreendido.

Quando o código não está disponível: você está documentando um sistema a partir da descrição fornecida no bloco de contexto acima, sinalizando tudo que não pode ser confirmado pelo código.

Sua missão é gerar um **PRD (Product Requirements Document)** definitivo, técnico, didático e completo — tão detalhado que **qualquer pessoa — dev júnior, PM, investidor, cliente ou estagiário — consiga entender, replicar e construir o sistema do zero, sem jamais ter tido acesso ao código original**.

---

## OBJETIVO DO DOCUMENTO

Transformar o projeto em um **manual vivo, auto-suficiente e replicável**:

- **Replicação do zero** em até 30 minutos em **qualquer ambiente**
- **Fork seguro** e **construção** sem quebrar nada
- **Manutenção sem medo** e entendimento de todas as decisões
- **Pitch de produto** em 5 slides
- **Treinamento de time** em 1 dia
- **Base para MVP, startup ou produto enterprise** totalmente independente do código original

---

## REGRA DE LACUNA

Quando uma informação não puder ser confirmada pelo código (ou não houver código disponível):

- **Não inventar** comportamento, fluxo ou configuração
- **Não deixar a seção vazia** sem explicação
- **Usar o marcador** `[NÃO IDENTIFICADO NO CÓDIGO]` para informações ausentes em projetos com código disponível
- **Usar o marcador** `[NÃO IMPLEMENTADO — requer definição]` para projetos sem código ou com código parcial
- Se a lacuna bloquear uma seção inteira, **parar e perguntar** antes de continuar:

´´´
--- INFORMAÇÃO NECESSÁRIA ---
Seção bloqueada: [nome da seção]
Perguntas:
1. [pergunta objetiva]
Aguardando resposta para continuar.
´´´

---

## ESTRUTURA OBRIGATÓRIA

*(Ordem fixa — todas as seções aplicáveis ao projeto)*

---

### 1. Visão Geral do Produto

- Nome oficial, versão atual (do `package.json`, `pyproject.toml`, `Cargo.toml`, `pom.xml` etc.)
- Slogan ou frase de impacto (se existir)
- Missão em 1 frase: **o que resolve e pra quem?**
- Personas com nome e dor (ex: "Lucas, dev backend, quer API sem boilerplate")
- Diferenciais vs concorrentes ou soluções manuais

---

### 2. Arquitetura de Alto Nível e Escolhas Tecnológicas

- Diagrama Mermaid completo do fluxo principal (ex: `Usuário → Frontend → API → Banco → Resposta`)
- Tecnologias principais e **por que foram escolhidas** (ex: Next.js → SSR + API routes; Go → performance; SQLite → simplicidade)
- Modelo de deploy (Docker, serverless, Kubernetes, bare metal, CLI, PWA etc.)
- **Padrões de Design** observados (ex: MVC, Clean Architecture, Repository Pattern, Factory)

---

### 3. Árvore de Diretórios e Esqueleto do Projeto

´´´
projeto/
├── src/             → código principal
├── tests/           → testes unitários/integração
├── public/          → assets estáticos
├── docker-compose.yml
└── .env.example
´´´

- Explicação de **cada pasta e arquivo crítico**: o que faz, quem usa, quando roda
- **Convenções de nomenclatura** de arquivos, componentes e funções (cruciais para replicação)

---

### 4. Requisitos Funcionais — O Catálogo de Ações

Formato:

´´´
RF-001: [nome da funcionalidade]
→ Ação do Usuário: [o que o usuário faz]
→ Fluxo de Código: [caminho técnico]
→ Módulo Crítico: [arquivo:linha]
→ Status: [Implementado / Parcial / Não implementado]
´´´

- Cobrir **todos os RFs identificáveis**, sem pular nada
- Para projetos sem código: listar RFs planejados com `Status: Não implementado`

---

### 5. Requisitos Não Funcionais — Metas de Qualidade

| Categoria | Requisito | Métrica | Target | Status |
|---|---|---|---|---|
| Performance | [ex: latência da API] | [ex: p95 < 200ms] | [valor] | [Implementado / A definir] |
| Segurança | [ex: autenticação] | [ex: JWT + refresh] | [valor] | [Implementado / A definir] |
| Escalabilidade | [ex: cache] | [ex: Redis TTL 5min] | [valor] | [Implementado / A definir] |
| Compatibilidade | [ex: Python 3.10+] | [versão mínima] | [valor] | [Implementado / A definir] |
| Usabilidade | [ex: acessibilidade WCAG] | [nível] | [valor] | [Implementado / A definir] |

---

### 6. Análise Técnica Profunda e Justificativa de Stack

Para **cada tecnologia usada**, responder:

- **O que é?**
- **Por que foi escolhida?** (vs alternativas rejeitadas)
- **Como funciona aqui?** (middleware, hook, lifecycle, uso de bibliotecas específicas)
- **Riscos?** (ex: memory leak, race condition)
- **Mitigação?** (ex: timeout, retry, circuit breaker)

Obrigatórias quando aplicáveis: framework, linguagem, banco de dados (versão + driver), cache, autenticação, build tool, containerização, CI/CD, testes.

---

### 7. Mapeamento Mestre de Rotas, Endpoints, Funções e Componentes Críticos

Para **cada rota, endpoint, função ou componente crítico**:

| Campo | Detalhe |
|---|---|
| Quem usa? | ex: frontend, admin, CLI, cron |
| Pra quê? | ex: gerar relatório, subir arquivo |
| Quando roda? | ex: após login, em background, ao iniciar |
| Lógica de negócio | passo a passo: valida input → chama serviço → grava log → retorna |
| O que acontece se falhar? | ex: 500, toast, retry, marcador de falha |
| Referência no código | arquivo + linha |
| Schema de Request/Response | exemplo JSON funcional (quando aplicável) |

---

### 8. Pipelines Especiais

Para cada pipeline identificado (RAG, ETL, CI/CD, WebSocket, background jobs, cron, WebRTC):

- Ciclo de vida completo (início → processamento → fim → falha)
- Configurações e dependências
- Fallback em caso de falha

---

### 9. Integrações Externas

Para cada integração (APIs, SDKs, serviços como Stripe, Google, AWS, Twilio):

- O que é e por que foi escolhida (com alternativa rejeitada, se identificável)
- Variáveis de ambiente **exatas** necessárias
- Como configurar (passo a passo)
- Como estender (ex: novo provedor de pagamento)
- Mocks ou stubs utilizados para desenvolvimento local

---

### 10. Segurança e Autenticação

- Fluxo completo: login → token → refresh → logout
- OAuth, JWT, cookies, PKCE, 2FA (mecanismos e como foram implementados)
- Proteções: CSRF, XSS, SQLi, rate limit, sanitização (bibliotecas e middlewares)
- Variáveis de ambiente sensíveis: explicar o uso de cada uma

---

### 11. Infraestrutura e DevOps

- Conteúdo do `docker-compose.yml`, Dockerfile e scripts de build críticos
- Variáveis obrigatórias e opcionais de ambiente (listagem completa e função de cada)
- Migrações, seeders, health checks (scripts e comandos exatos)
- Diferenças entre ambientes (local vs produção)
- Monitoramento, logs, alertas (ferramentas e formatos)

---

### 12. Extensibilidade e Customização

- Plugins, middlewares, hooks, configurações dinâmicas
- Como criar um módulo/plugin em 5 passos (tutorial)
- Exemplos reais no código

---

### 13. Limitações Conhecidas

- Bugs identificados, com severidade e workaround
- Race conditions, memory leaks ou problemas de concorrência
- Formatos não suportados, limites de entrada
- Dependências obsoletas ou vulneráveis

---

### 14. Roadmap Inferido

Baseado nas limitações e na arquitetura atual:

| Versão | Foco | Features Principais | Estimativa |
|---|---|---|---|

---

### 15. Guia Mestre de Replicação

Passo a passo independente e autocontido:

1. **Pré-requisitos completos** (linguagens com versão exata, ferramentas, SDKs, gerenciadores de pacote)
2. `git clone ...` (instrução simulada com URL placeholder)
3. **Inicialização de banco/infra** (se aplicável)
4. Instalar dependências (comando **exato**)
5. Configurar `.env` (instruções por variável)
6. Build (comando **exato**)
7. Execução (comando **exato**)
8. Testes (como rodar + como validar manualmente a funcionalidade principal)
9. Acesso à interface ou API (URLs, portas, credenciais padrão)
10. Verificação pós-deploy (health check, smoke test)

---

## INSTRUÇÕES DE INTEGRAÇÃO COM O SISTEMA DE ARQUIVAMENTO

Após este PRD ser gerado e aprovado, ele alimenta o Sistema de Arquivamento Progressivo (Comando 1 — Protocolo de Arquivamento v1.1). O mapeamento é:

| Seção do PRD | Destino no Arquivamento |
|---|---|
| Seções 1-2 (Visão, Arquitetura) | `CURRENT_STATE.md` — estado inicial do projeto |
| Seção 6 (Justificativa de Stack) | `DECISION_LOG.md` — decisões da Fase 0 (planejamento) |
| Seção 14 (Roadmap) | `BACKLOG_FUTURO.md` — ondas e critérios de aceite |
| Seção 3 (Árvore de Diretórios) | `CURRENT_STATE.md` — módulos e contratos vigentes |
| Seção 4 (RFs) | `BACKLOG_FUTURO.md` — funcionalidades por fase |

Ao executar o Comando 1 logo após aprovar este PRD, instrua a IA a usar essas seções como insumo direto em vez de ler blueprints históricos — o PRD recém-gerado já é o estado inicial consolidado.

---

## REGRAS DE GERAÇÃO

1. Gere até o limite de tokens
2. Ao parar, encerre com: `--- CONTINUAÇÃO PENDENTE (próximo: [seção]) ---`
3. O usuário dirá "continue" para retomar
4. Use markdown, tabelas, Mermaid, blocos de código
5. Seja técnico, didático e preciso
6. Baseado 100% no código disponível — sem achismo
7. Se não souber: use o marcador correto (`[NÃO IDENTIFICADO NO CÓDIGO]` ou `[NÃO IMPLEMENTADO]`) ou pare e pergunte. Esta regra tem precedência sobre a regra 1.
8. **Foco na replicação:** cada passo ou informação técnica deve incluir o contexto necessário para que um desenvolvedor reproduza o ambiente sem acesso ao código original

**GERE O DOCUMENTO AGORA.**