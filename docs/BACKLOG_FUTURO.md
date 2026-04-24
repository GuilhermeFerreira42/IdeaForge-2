# BACKLOG ESTRATÉGICO — IdeaForge 2

## Intenção Original
- **Objetivo:** Sistema que recebe ideia bruta, executa debate adaptativo entre agentes e gera Relatório de Ideia Validada como contrato de interface para geração de PRD por modelo grande.
- **Estado Atual:** Fase 1 (Concluída) | 23/04/2026. Fundação de dados implantada.
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
| W2-01 | ProponentAgent modo expansão | Round 0: transformar ideia bruta em proposta estruturada de 7 seções | `agents/proponent_agent.py` | Teste com MockProvider: proposta gerada tem ≥7 seções não-vazias | PENDENTE |
| W2-02 | CriticAgent refatorado | Remover lógica PRD, focar em debate puro contra proposta | `agents/critic_agent.py` | Teste com MockProvider: crítica gera issues parseáveis pelo tracker | PENDENTE |
| W2-03 | Specialist Profiles | Banco de agentes especializados pré-definidos (Security, Feasibility, Scalability, UX) | `agents/specialist_profiles.py` | Teste: perfis carregam corretamente, prompts são válidos | PENDENTE |
| W2-04 | DebateEngine refatorado | Integrar orquestrador adaptativo, usar tracker como ponte exclusiva, remover truncamentos | `debate/debate_engine.py` | Teste integração: debate completo com MockProvider, rounds dinâmicos, spawning funcional | PENDENTE |
| W2-05 | Prompt Templates | Novos templates para debate v2: expansão, defesa, crítica, síntese | `core/prompt_templates.py` | Templates substituem os antigos, sem referência a PRD | PENDENTE |

### Meta da Onda 2
- **Critério binário:** `pytest tests/integration/test_debate_flow.py -v` e `pytest tests/integration/test_agent_spawning.py -v` passam
- **Status:** PENDENTE

---

## Onda 3 — Síntese, Relatório e CLI (Fase 5)

| ID | Técnica/Feature | Descrição | Arquivos Impactados | Critério de Aceite | Status |
|---|---|---|---|---|---|
| W3-01 | SynthesizerAgent | Juíza neutra que recebe quadro de validações e gera relatório em Markdown | `agents/synthesizer_agent.py` | Teste com MockProvider: relatório tem todas as seções obrigatórias e ≥3000 chars | PENDENTE |
| W3-02 | ReportGenerator | Montagem do relatório final com fallback (dump do ValidationBoard se Synthesizer falhar) | `core/report_generator.py` | Teste: fallback gera relatório mínimo preservando 100% dos dados | PENDENTE |
| W3-03 | Controller refatorado | Pipeline simplificado: Round 0 → Debate → Síntese → Persistência | `core/controller.py` | Teste integração: pipeline completo com MockProvider sem crash | PENDENTE |
| W3-04 | CLI simplificada | Entry point com flags --idea, --constraint, --interactive, --model | `cli/main.py` | CLI funcional em ≤3 comandos para primeira execução | PENDENTE |
| W3-05 | Smoke test real | Execução completa com gpt-oss:20b-cloud, validação de relatório | `tests/smoke/` | 3 execuções consecutivas sem crash, relatório legível e coerente | PENDENTE |

### Meta da Onda 3
- **Critério binário:** `pytest tests/ -v` passa (unitários + integração + smoke) e relatório gerado alimentado a Claude/Gemini produz PRD de qualidade
- **Status:** PENDENTE

---

## Regras do Backlog
1. Itens movem de `PENDENTE` para `CONCLUÍDO` apenas após validação com critério binário
2. Nenhuma Onda inicia sem a anterior concluída
3. Novas técnicas descobertas durante implementação são adicionadas como item novo na Onda apropriada