# Blueprint — Fase 0: Limpeza e Preparação do IdeaForge 2

**Fase:** 0
**Nome:** Limpeza Cirúrgica e Estruturação do Repositório
**Onda:** Pré-Onda (preparação)
**Pré-requisito:** PRD aprovado, Protocolo de Arquivamento executado
**Duração estimada:** 1 sessão

---

## Objetivo

Preparar o repositório para o início da implementação, removendo todo código PRD-specific do IdeaForge v1, eliminando documentação obsoleta e garantindo que a estrutura final contenha **apenas** infraestrutura reutilizável + documentação do v2.

**Ao final desta fase:** O repositório está limpo, commitável e pronto para o GitHub como base do IdeaForge 2, sem nenhum vestígio de lógica PRD.

---

## Ações — Ordem de Execução

### AÇÃO 1: Deletar pasta `workflow/`

O workflow já está embutido nos docs do projeto (`.ai-context`, `.humano`, `ARCHIVING_PROTOCOL.md`).

```
DELETAR:
  workflow/🟢 GERAR DOCUMENTACAO PRD.md
  workflow/⭐ Protocolo NEXUS.md
  workflow/👍 Protocolo - Sistema de Arquivamento Progressivo 1.1.md
  workflow/                                    ← remover diretório inteiro
```

---

### AÇÃO 2: Deletar `docs/archive/`

Histórico de fases do v1. Não tem valor para o v2 — fica no repo antigo como referência.

```
DELETAR:
  docs/archive/PHASE_0/
  docs/archive/PHASE_1/
  docs/archive/PHASE_2/
  docs/archive/PHASE_3/
  docs/archive/PHASE_4/
  docs/archive/PHASE_5/
  docs/archive/phase_07/
  docs/archive/phase_07.1/
  docs/archive/phase_08/
  docs/archive/phase_09/
  docs/archive/phase_10/
  docs/archive/phase_9.1/
  docs/archive/phase_9.1.1/
  docs/archive/phase_9.2/
  docs/archive/phase_9.3/
  docs/archive/phase_9.4/
  docs/archive/phase_9.5/
  docs/archive/phase_9.5.1/
  docs/archive/phase_9.5.3/
  docs/archive/9.6.resolved
  docs/archive/Blueprint Técnico — IdeaForge CLI.resolved
  docs/archive/                                ← remover diretório inteiro
```

> **Nota:** Criar `docs/archive/` vazio com um `.gitkeep` para que o protocolo de arquivamento funcione nas fases futuras.

---

### AÇÃO 3: Deletar código PRD-specific de `agents/`

```
DELETAR:
  src/agents/architect_agent.py                (3.661 bytes — System Design para PRD)
  src/agents/consistency_checker_agent.py       (8.651 bytes — Audit de PRD)
  src/agents/product_manager_agent.py           (10.311 bytes — Consolidação de PRD)
  src/agents/security_reviewer_agent.py         (4.115 bytes — Security Review para PRD)

MANTER:
  src/agents/proponent_agent.py                 (2.946 bytes — será refatorado na Fase 3)
  src/agents/critic_agent.py                    (8.454 bytes — será refatorado na Fase 3)
```

---

### AÇÃO 4: Deletar código PRD-specific de `core/`

```
DELETAR:
  src/core/sectional_generator.py              (37.206 bytes — Core NEXUS 20 passes)
  src/core/context_extractors.py                (6.259 bytes — Extratores para seções PRD)
  src/core/output_validator.py                  (10.560 bytes — Validador de PRD)
  src/core/golden_examples.py                   (9.375 bytes — Exemplars de PRD)
  src/core/section_quality_checker.py           (8.514 bytes — Quality checker de seções)
  src/core/exemplars/                           (diretório inteiro — 13 arquivos de padrões PRD)

MANTER:
  src/core/artifact_store.py                    (7.185 bytes — infraestrutura genérica)
  src/core/blackboard.py                        (3.324 bytes — infraestrutura genérica)
  src/core/controller.py                        (12.035 bytes — será REESCRITO na Fase 5)
  src/core/pipeline_logger.py                   (7.587 bytes — infraestrutura genérica)
  src/core/planner.py                           (18.403 bytes — será REESCRITO na Fase 5)
  src/core/prompt_templates.py                  (17.478 bytes — será REESCRITO na Fase 3)
  src/core/stream_handler.py                    (15.902 bytes — infraestrutura genérica)
```

---

### AÇÃO 5: Deletar pasta `planning/`

```
DELETAR:
  src/planning/plan_generator.py                (2.182 bytes — Development Plan para PRD)
  src/planning/                                 ← remover diretório inteiro
```

---

### AÇÃO 6: Deletar testes antigos do v1

```
DELETAR:
  tests/                                        ← conteúdo inteiro (se existir)

CRIAR:
  tests/__init__.py                             (vazio)
  tests/conftest.py                             (placeholder com MockProvider básico)
  tests/unit/.gitkeep
  tests/integration/.gitkeep
  tests/smoke/.gitkeep
  tests/fixtures/.gitkeep
```

---

### AÇÃO 7: Deletar `docs/README.md` antigo

```
DELETAR:
  docs/README.md                                (4.299 bytes — README do v1)
```

O README do projeto será o README.md na raiz (se existir) ou será criado na Fase 5.

---

### AÇÃO 8: Verificar que `docs/` está limpo

Após as ações acima, `docs/` deve conter APENAS:

```
docs/
├── PRD.md                          ← PRD do IdeaForge 2 (aprovado)
├── CURRENT_STATE.md                ← Estado atual (Fase 0)
├── DECISION_LOG.md                 ← Decisões da Fase 0
├── BACKLOG_FUTURO.md               ← Roadmap com 3 ondas
├── ARCHIVING_PROTOCOL.md           ← Protocolo de arquivamento
├── fase_0_blueprint.md             ← ESTE DOCUMENTO (será arquivado)
└── archive/
    └── .gitkeep                    ← Pasta vazia para fases futuras
```

---

### AÇÃO 9: Criar `tests/conftest.py` com MockProvider

```python
"""
Fixtures compartilhadas para testes do IdeaForge 2.
MockProvider permite testar todo o pipeline sem chamar LLM.
"""
import pytest


class MockProvider:
    """Provider de LLM fake para testes TDD."""

    def __init__(self, responses=None):
        self.responses = responses or {}
        self.call_log = []

    def generate(self, prompt, context=None, role="user", max_tokens=None, think=False):
        self.call_log.append({
            "prompt": prompt[:200],
            "role": role,
            "max_tokens": max_tokens,
        })
        if callable(self.responses):
            return self.responses(prompt)
        return self.responses.get(role, "Mock response for: " + role)


@pytest.fixture
def mock_provider():
    """Fixture que retorna um MockProvider limpo."""
    return MockProvider()


@pytest.fixture
def mock_provider_with_responses():
    """Fixture factory para MockProvider com respostas customizadas."""
    def _factory(responses):
        return MockProvider(responses=responses)
    return _factory
```

---

### AÇÃO 10: Atualizar CURRENT_STATE.md e DECISION_LOG.md

Após a limpeza:

**CURRENT_STATE.md** — atualizar a tabela de módulos removendo os deletados e marcando Fase 0 como concluída.

**DECISION_LOG.md** — adicionar:
```
F0 | DEL | Removidos 4 agents PRD-specific (architect, consistency_checker, product_manager, security_reviewer) | PRD-specific, sem uso no debate-only | src/agents/
F0 | DEL | Removidos 5 arquivos core PRD-specific + exemplars/ | NEXUS passes, extratores e validadores de PRD | src/core/
F0 | DEL | Removida pasta planning/ (plan_generator.py) | Development Plan era PRD-specific | src/planning/
F0 | DEL | Removidos docs/archive/ e workflow/ | Histórico v1 fica no repo antigo; workflow embutido nos docs | docs/, workflow/
F0 | ADD | Criado tests/conftest.py com MockProvider | Base para TDD em todas as fases futuras | tests/
```

---

## Inventário Final — O que FICA no repositório após Fase 0

```
idea-forge/
├── .ai-context
├── .humano
├── .gitignore
├── iniciar.bat
│
├── docs/
│   ├── PRD.md
│   ├── CURRENT_STATE.md
│   ├── DECISION_LOG.md
│   ├── BACKLOG_FUTURO.md
│   ├── ARCHIVING_PROTOCOL.md
│   └── archive/
│       └── .gitkeep
│
├── idea-forge/
│   └── src/
│       ├── agents/
│       │   ├── proponent_agent.py          (será refatorado Fase 3)
│       │   └── critic_agent.py              (será refatorado Fase 3)
│       │
│       ├── cli/
│       │   └── main.py                      (será reescrito Fase 5)
│       │
│       ├── config/
│       │   └── settings.py
│       │
│       ├── conversation/
│       │   └── conversation_manager.py
│       │
│       ├── core/
│       │   ├── artifact_store.py            ✅ infraestrutura
│       │   ├── blackboard.py                ✅ infraestrutura
│       │   ├── controller.py                (será reescrito Fase 5)
│       │   ├── pipeline_logger.py           ✅ infraestrutura
│       │   ├── planner.py                   (será reescrito Fase 5)
│       │   ├── prompt_templates.py          (será reescrito Fase 3)
│       │   └── stream_handler.py            ✅ infraestrutura
│       │
│       ├── debate/
│       │   ├── debate_engine.py             (será refatorado Fase 4)
│       │   └── debate_state_tracker.py      (será expandido Fase 1)
│       │
│       └── models/
│           ├── model_provider.py            ✅ interface
│           ├── ollama_provider.py           ✅ provider
│           └── cloud_provider.py            ✅ provider
│
└── tests/
    ├── __init__.py
    ├── conftest.py                          ✅ MockProvider
    ├── unit/.gitkeep
    ├── integration/.gitkeep
    ├── smoke/.gitkeep
    └── fixtures/.gitkeep
```

**Total de arquivos de código:** 14 (vs ~27 no v1 = **48% removido**)
**Total de bytes removidos:** ~111.398 bytes (~109 KB de código PRD deletado)

---

## Critério de Aceite da Fase 0

| # | Check | Verificação |
|---|---|---|
| 1 | Nenhum arquivo PRD-specific existe em `src/` | `grep -r "sectional\|NEXUS_FINAL\|consolidate_prd" src/` retorna vazio |
| 2 | `docs/archive/` contém apenas `.gitkeep` | `ls docs/archive/` mostra 1 arquivo |
| 3 | `workflow/` não existe | `ls workflow/` falha |
| 4 | `tests/conftest.py` existe com MockProvider | `python -c "from tests.conftest import MockProvider"` funciona |
| 5 | Arquivos mantidos não foram modificados | Diff dos 8 arquivos ✅ infraestrutura = zero mudanças |
| 6 | `docs/CURRENT_STATE.md` atualizado para Fase 0 | Fase 0 marcada como concluída |
| 7 | `docs/DECISION_LOG.md` tem entradas da Fase 0 | 5 linhas novas de DEL + ADD |

---

## Commit Sugerido

```
[FASE 0] LIMPEZA CIRÚRGICA — remoção de código PRD-specific e preparação do repositório IdeaForge 2
```
