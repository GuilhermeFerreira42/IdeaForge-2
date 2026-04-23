# CURRENT_STATE — IdeaForge 2
> Última atualização: Fase 0 (Concluída) | 23/04/2026

## Arquitetura Ativa
- **Padrão:** Blackboard + Orquestrador Adaptativo (regras programáticas, zero LLM)
- **Pipeline:** Ideia Bruta → Round 0 (expansão) → Debate Adaptativo (N rounds) → Síntese (juíza neutra) → Relatório de Ideia Validada
- **Persistência:** ArtifactStore (Markdown versionado) + Blackboard (JSON)
- **LLM:** Ollama local via HTTP (`OllamaProvider`) ou cloud (`CloudProvider`)

## Módulos e Contratos Vigentes
| Módulo | Arquivo | Contrato Público | Desde |
|---|---|---|---|
| DebateEngine | `debate/debate_engine.py` | `run_debate(idea, context) → transcript` | v1 (refatorar) |
| DebateStateTracker | `debate/debate_state_tracker.py` | `extract_issues(text) → List[IssueRecord]` | v1 (expandir) |
| ProponentAgent | `agents/proponent_agent.py` | `expand(idea) → proposta` / `defend(issues, critique) → defesa` | v1 (adicionar modo) |
| CriticAgent | `agents/critic_agent.py` | `review(artifact, context) → crítica` | v1 (simplificar) |
| SynthesizerAgent | `agents/synthesizer_agent.py` | `synthesize(board, idea, stats) → relatório` | v2 [NOVO] |
| AdaptiveOrchestrator | `core/adaptive_orchestrator.py` | `evaluate(tracker) → CONTINUE/STOP/SPAWN` | v2 [NOVO] |
| ValidationBoard | `core/validation_board.py` | `update(text) → {issues, decisions, assumptions}` | v2 [NOVO] |
| ConvergenceDetector | `core/convergence_detector.py` | `is_converged(tracker, rounds) → bool` | v2 [NOVO] |
| ReportGenerator | `core/report_generator.py` | `generate(board, idea, transcript) → markdown` | v2 [NOVO] |
| Blackboard | `core/blackboard.py` | `get/set(key, value)` | v1 (mantido) |
| ArtifactStore | `core/artifact_store.py` | `write(name, content) / read(name) → str` | v1 (mantido) |
| StreamHandler | `core/stream_handler.py` | `stream(response) → chunks` | v1 (mantido) |
| ModelProvider | `models/model_provider.py` | `generate(prompt, context) → str` (ABC) | v1 (mantido) |

## Fluxo Principal
1. CLI recebe ideia + constraints → Controller
2. ProponentAgent.expand(ideia) → Proposta Estruturada (Round 0)
3. Usuário valida proposta (max `MAX_EXPANSION_RETRIES` ajustes)
4. ValidationBoard registra premissas como UNTESTED
5. Loop: Proponent defende → Critic ataca → Tracker atualiza → Orquestrador avalia
6. Orquestrador: CONTINUE (issues HIGH) / SPAWN (≥3 mesma categoria) / STOP (convergência ou MAX_ROUNDS)
7. SynthesizerAgent recebe quadro (~2300 chars) → Relatório de Ideia Validada
8. ArtifactStore persiste relatório + transcript

## Invariantes Globais (nunca violar)
1. Orquestrador é 100% programático — zero chamadas LLM para decisões de fluxo
2. Agentes NUNCA recebem transcript acumulado — apenas: ideia + tracker + última resposta
3. MAX_ROUNDS=10, MAX_AGENTS=5, MIN_ROUNDS=2, MAX_EXPANSION_RETRIES=3 (configuráveis, mas sempre com limite)
4. Decisões VALIDATED não são rediscutidas em rounds subsequentes
5. Issues RESOLVED não são reabertos
6. Parser degrada graciosamente: tabela → bullets → heurística (nunca crasha)
7. Se artefato não encontrado → PARAR e reportar, nunca fallback silencioso
8. Testes escritos ANTES do código (TDD)
9. Similaridade de convergência usa Jaccard com stopwords PT (zero LLM)

## Restrições Técnicas Ativas
| Parâmetro | Valor | Configurável |
|---|---|---|
| Input do agente | ≤ 3000 chars | Sim |
| Output do modelo | num_predict dinâmico | Sim |
| Overhead de orquestração | ≤ 500ms entre rounds | Sujeito a revisão |
| Convergência threshold | Jaccard > 0.7 | Sim |
| Spawn threshold | ≥ 3 issues mesma categoria | Sim |

## Testes Obrigatórios
| Suite | Diretório | Cobertura | Comando |
|---|---|---|---|
| Unitários | `tests/unit/` | ≥ 80% módulos core | `pytest tests/unit/ -v` |
| Integração | `tests/integration/` | Fluxo completo com MockProvider | `pytest tests/integration/ -v` |
| Smoke | `tests/smoke/` | 1 execução real com modelo | `pytest tests/smoke/ -v --timeout=600` |

## Dependências Externas
| Pacote | Versão | Motivo |
|---|---|---|
| requests | 2.28+ | HTTP para Ollama API |
| pytest | 7.0+ | Framework de testes TDD |
