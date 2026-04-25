# BACKLOG ESTRATÉGICO — IdeaForge 2

## Intenção Original
- **Objetivo:** Sistema que recebe ideia bruta, executa debate adaptativo entre agentes e gera Relatório de Ideia Validada como contrato de interface para geração de PRD por modelo grande.
- **Estado Atual:** Onda 2 (Concluída) | 25/04/2026. Motor de debate funcional.
- **Meta Final:** Pipeline debate-only estável, testado com gpt-oss:20b-cloud, gerando relatórios que um modelo grande transforma em PRD completo.

---

## Onda 1 — Fundação e Core (Fases 1-2)

| ID | Técnica/Feature | Descrição | Arquivos Impactados | Critério de Aceite | Status |
|---|---|---|---|---|---|
| W1-01 | Branch + Limpeza | Criar branch v2-debate-only, deletar ~12 arquivos PRD-specific | Todo o repositório | Branch existe, arquivos PRD removidos, infra preservada intacta | CONCLUÍDO |
| W1-02 | ValidationBoard | Quadro expandido com Issues + Decisões + Pressupostos, 3 tipos de registro com transições de estado | `core/validation_board.py` | Testes unitários passando: criar/atualizar/consultar os 3 tipos de registro | CONCLUÍDO |
| W1-03 | DebateStateTracker expandido | Parser de 3 níveis (tabela → bullets → heurística), extração de decisões e pressupostos | `debate/debate_state_tracker.py` | Testes com fixtures: ≥80% issues capturados em tabela, ≥60% em texto livre | CONCLUÍDO |
| W1-04 | ConvergenceDetector | Jaccard similarity com stopwords PT, threshold 0.7, detecção de convergência por 2 rounds sem issues novos | `core/convergence_detector.py` | Testes unitários: textos iguais→1.0, textos diferentes→<0.3, convergência detectada corretamente | CONCLUÍDO |
| W1-05 | AdaptiveOrchestrator | Lógica de CONTINUE/STOP/SPAWN baseada no tracker, limites rígidos, fallback para rounds fixos | `core/adaptive_orchestrator.py` | Testes: issues HIGH→CONTINUE, convergência→STOP, ≥3 mesma categoria→SPAWN, MAX_AGENTS→bloqueio | CONCLUÍDO |

### Meta da Onda 1
- **Critério binário:** `pytest tests/unit/ -v` passa com 100% nos 5 módulos acima + `pytest tests/integration/test_adaptive_rounds.py -v` passa
- **Status:** CONCLUÍDO

---

## Onda 2 — Agentes e Debate (Fases 3-4)

| ID | Técnica/Feature | Descrição | Arquivos Impactados | Critério de Aceite | Status |
|---|---|---|---|---|---|
| W2-01 | ProponentAgent modo expansão | Round 0: transformar ideia bruta em proposta estruturada de 7 seções | `src/agents/proponent_agent.py` | Teste com MockProvider: proposta gerada tem ≥7 seções não-vazias | CONCLUÍDO |
| W2-02 | ContextBuilder | Truncamento determinístico (≤3000 chars) e montagem de prompts | `src/debate/context_builder.py` | Garantir limite rígido e prioridade de budgets [COR-13] | CONCLUÍDO |
| W2-03 | CriticAgent refatorado | Remover lógica PRD, focar em debate puro contra proposta | `src/agents/critic_agent.py` | Teste com MockProvider: crítica gera issues parseáveis pelo tracker | CONCLUÍDO |
| W2-04 | Specialist Profiles | Banco de agentes especializados pré-definidos (Security, Feasibility, Scalability) | `src/agents/specialist_profiles.py` | Teste: perfis carregam corretamente, prompts são válidos | CONCLUÍDO |
| W2-05 | RoundExecutor | Execução de turnos, canonicalização e aplicação de patches | `src/debate/round_executor.py` | Teste: patches aplicados na proposta, parsing detecta falhas (COR-14) | CONCLUÍDO |
| W2-06 | DebateEngine | Integração completa do loop de debate adaptativo | `src/debate/debate_engine.py` | Teste integração: fluxo Round 0 → N Rounds funcional | CONCLUÍDO |

### Meta da Onda 2
- **Critério binário:** `pytest tests/integration/test_debate_flow.py -v` passa com 100% de sucesso.
- **Status:** CONCLUÍDO

---

## Onda 3 — Síntese, Relatório e CLI (Fase 5)

| ID | Técnica/Feature | Descrição | Arquivos Impactados | Critério de Aceite | Status |
|---|---|---|---|---|---|
| W3-01 | SynthesizerAgent | Juíza neutra que recebe quadro de validações e gera relatório em Markdown | `src/agents/synthesizer_agent.py` | Teste com MockProvider: relatório tem Executive Summary, Riscos e Decisões | PENDENTE |
| W3-02 | ReportGenerator | Montagem do relatório final com fallback (dump do ValidationBoard se Synthesizer falhar) | `src/core/report_generator.py` | Teste: fallback gera relatório mínimo preservando 100% dos dados | PENDENTE |
| W3-03 | Controller refatorado | Pipeline simplificado: Round 0 → Debate → Síntese → Persistência | `src/core/controller.py` | Teste integração: pipeline completo com MockProvider sem crash | PENDENTE |
| W3-04 | CLI simplificada | Entry point com flags --idea, --interactive, --model | `src/cli/main.py` | CLI funcional em ≤3 comandos para primeira execução | PENDENTE |
| W3-05 | Smoke test real | Execução completa com modelo real, validação de relatório | `tests/smoke/` | 3 execuções consecutivas sem crash, relatório legível e coerente | PENDENTE |

### Meta da Onda 3
- **Critério binário:** `pytest tests/ -v` passa (unitários + integração + smoke) e relatório gerado produz PRD de qualidade se alimentado a outro modelo.
- **Status:** PENDENTE

### CONTRATOS_DA_ONDA 3 [CONFIRMADO]

```yaml
OUTPUT_SCHEMAS:
  W3-01: Relatório com seções: # Sumário Executivo, ## Decisões Validadas, ## Issues Pendentes, ## Matriz de Risco, ## Veredito.
  W3-02: Fallback Dump (Texto plano de todos os registros do Board se o LLM falhar).

ESCOPO_CONGELADO:
  - src/debate/ (Motor validado na Onda 2)
  - src/core/validation_board.py
  - src/core/adaptive_orchestrator.py

NOVOS:
  - src/cli/main.py: NOVO
  - src/core/controller.py: NOVO

SPECIALISTS_MVP: Resolvido na Onda 2 — Security, Scalability, Feasibility, Completeness implementados em src/agents/specialist_profiles.py

DECISOES_EXTRAS:
  - O SynthesizerAgent deve ser proibido de inventar dados: se não está no Board, não está no relatório.
  - Implementar flag `--debug` na CLI para expor o transcript e o board JSON.
```

---

## Regras do Backlog
1. Itens movem de `PENDENTE` para `CONCLUÍDO` apenas após validação com critério binário
2. Nenhuma Onda inicia sem a anterior concluída
3. `CONTRATOS_DA_ONDA` deve estar confirmado pelo usuário antes de disparar o NEXUS — nunca durante
4. A IA propõe o `CONTRATOS_DA_ONDA` — o usuário valida.