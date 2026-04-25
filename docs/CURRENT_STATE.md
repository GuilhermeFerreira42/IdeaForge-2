# CURRENT_STATE — IdeaForge 2
> Fase 2 concluída | Motor de debate funcional | Onda 3 pendente | 25/04/2026

## Arquitetura Ativa
- **Padrão:** Blackboard + Orquestrador Adaptativo + RoundExecutor.
- **Pipeline implementado:** Ideia Bruta → Round 0 (expansão 7 seções) → Debate Adaptativo (N rounds) → [PENDENTE: Síntese + Relatório].
- **Código ativo:** `src/` (NÃO `idea-forge/src/`, que é legado v1 congelado).
- **LLM:** Ollama local via HTTP (`OllamaProvider`) ou cloud (`CloudProvider`).

## Módulos Vigentes (código que existe e funciona)
| Módulo | Arquivo | Contrato Público | Fase |
|---|---|---|---|
| DebateEngine | `src/debate/debate_engine.py` | `run_debate(idea) → DebateResult` | F2 |
| RoundExecutor | `src/debate/round_executor.py` | `execute_critic_round(), execute_defense_round()` | F2 |
| ContextBuilder | `src/debate/context_builder.py` | `build_defense_prompt(), build_critique_prompt()` | F2 |
| DebateStateTracker | `src/debate/debate_state_tracker.py` | `extract_issues_from_critique(), extract_resolutions()` | F1 |
| ProponentAgent | `src/agents/proponent_agent.py` | `expand(idea), defend(prompt)` | F2 |
| CriticAgent | `src/agents/critic_agent.py` | `review(prompt)` | F2 |
| SpecialistProfiles | `src/agents/specialist_profiles.py` | `get_profile(cat), build_specialist_prompt()` | F2 |
| prompt_templates | `src/core/prompt_templates.py` | `PT_EN_NORMALIZATION_MAP`, Templates v2 | F2 |
| AdaptiveOrchestrator | `src/core/adaptive_orchestrator.py` | `evaluate(round, current, previous, count)` | F1 |
| ValidationBoard | `src/core/validation_board.py` | `add_*, get_*_prompt(), snapshot()` | F1 |
| ConvergenceDetector | `src/core/convergence_detector.py` | `is_converged(current, previous, count, round)` | F1 |
| ModelProvider | `src/models/model_provider.py` | `generate(prompt, context) → str` (ABC) | F0 |

## Fluxo Principal (estado real)
1. `DebateEngine.run_debate(ideia)` detecta se é ideia bruta → `ProponentAgent.expand()` (Round 0).
2. Loop de debate: `RoundExecutor.execute_critic_round()` → `Orquestrador.evaluate()` → `execute_defense_round()`.
3. Orquestrador decide: CONTINUE / SPAWN (Especialista) / STOP (convergência ou MAX_ROUNDS).
4. **Passo seguinte (Onda 3):** SynthesizerAgent + ReportGenerator + CLI.

## Invariantes Globais
1. Orquestrador 100% programático — zero LLM para decisões de fluxo.
2. Agentes recebem apenas: proposta vigente + issues + última defesa/crítica (nunca transcript).
3. Prompt ≤ 3000 chars (truncamento determinístico via ContextBuilder).
4. Decisões VALIDATED não são rediscutidas; Issues RESOLVED não são reabertos.
5. Parser degrada: Tabela 4 colunas → Bullets → Heurística keyword.
6. TDD: testes escritos ANTES do código.

## Testes (90 testes, 100% passando)
| Suite | Comando |
|---|---|
| Unitários (74 testes) | `pytest tests/unit/ -v` |
| Integração (6 testes) | `pytest tests/integration/ -v` |
| Tudo | `pytest tests/ -v` |

## Nota sobre `idea-forge/src/`
Diretório legado da v1. Contém código PRD-specific congelado (controller, planner, stream_handler). **Não é o código ativo do IdeaForge 2.** O código ativo está em `src/`.
