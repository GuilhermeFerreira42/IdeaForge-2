# CURRENT_STATE — IdeaForge 2
> Última atualização: Fase 2 (Concluída - Agentes e Motor de Debate) | 25/04/2026

## Arquitetura Ativa
- **Padrão:** Blackboard + Orquestrador Adaptativo + RoundExecutor (Decomposição COR-10).
- **Pipeline:** Ideia Bruta → Round 0 (expansão) → Debate Adaptativo (N rounds) → Síntese (juíza neutra) → Relatório de Ideia Validada.
- **Persistência:** ArtifactStore (Markdown versionado) + ValidationBoard (JSON/Blackboard).
- **LLM:** Ollama local via HTTP (`OllamaProvider`) ou cloud (`CloudProvider`).

## Módulos e Contratos Vigentes
| Módulo | Arquivo | Contrato Público | Desde |
|---|---|---|---|
| DebateEngine | `src/debate/debate_engine.py` | `run_debate(idea_or_proposal) → DebateResult` | v2 (Concluído) |
| RoundExecutor | `src/debate/round_executor.py` | `execute_critic_round(), execute_defense_round()` | v2 [NOVO] |
| ContextBuilder | `src/debate/context_builder.py` | `build_defense_prompt(), build_critique_prompt()` | v2 [NOVO] |
| DebateStateTracker | `src/debate/debate_state_tracker.py` | `extract_issues_from_critique(), extract_resolutions()` | v1/v2 |
| ProponentAgent | `src/agents/proponent_agent.py` | `expand(idea), defend(prompt)` | v2 (Refatorado) |
| CriticAgent | `src/agents/critic_agent.py` | `review(prompt)` | v2 (Refatorado) |
| SpecialistProfiles | `src/agents/specialist_profiles.py` | `get_profile(cat), build_specialist_prompt()` | v2 [NOVO] |
| prompt_templates | `src/core/prompt_templates.py` | `PT_EN_NORMALIZATION_MAP`, Templates v2 | v2 [NOVO] |
| SynthesizerAgent | `src/agents/synthesizer_agent.py` | `synthesize(board, idea, stats)` | v2 (Pendente) |
| AdaptiveOrchestrator | `src/core/adaptive_orchestrator.py` | `evaluate(round, current, previous, count)` | v1/v2 |
| ValidationBoard | `src/core/validation_board.py` | `add_*, get_*_prompt(), snapshot()` | v1/v2 |
| ConvergenceDetector | `src/core/convergence_detector.py` | `is_converged(current, previous, count, round)` | v1/v2 |
| ModelProvider | `src/models/model_provider.py` | `generate(prompt, context) → str` (ABC) | v1 (Mantido) |

## Fluxo Principal
1. CLI recebe ideia → ProponentAgent.expand(ideia) → Proposta Round 0 (7 seções).
2. ValidationBoard inicializa premissas.
3. Turno Crítico: ContextBuilder monta prompt (≤3000 chars) → CriticAgent → Tracker (Canonicalização v2).
4. Orquestrador: CONTINUE / SPAWN (Especialista) / STOP (Convergência ou MAX_ROUNDS).
5. Turno Defesa: Proponent defende → RoundExecutor aplica patches na Proposta Vigente.
6. Loop se repete até decisão do Orquestrador.
7. [PENDENTE] SynthesizerAgent gera Relatório de Ideia Validada.

## Invariantes Globais (nunca violar)
1. Orquestrador é 100% programático — zero chamadas LLM para decisões de fluxo.
2. Agentes NUNCA recebem transcript acumulado — apenas: proposta vigente + issues + última defesa/crítica.
3. Máximo 3000 caracteres no prompt de entrada dos agentes (truncamento determinístico).
4. Decisões VALIDATED não são rediscutidas; Issues RESOLVED não são reabertos.
5. Parser degrada graciosamente: Tabela 4 colunas → Bullets → Heurística.
6. Atomicidade: ValidationBoard só muta após parsing bem-sucedido do turno.
7. Testes escritos ANTES do código (TDD).

## Testes Obrigatórios
| Suite | Diretório | Cobertura | Comando |
|---|---|---|---|
| Unitários | `tests/unit/` | 100% Agentes e Motor | `pytest tests/unit/ -v` |
| Integração | `tests/integration/` | Fluxo completo do debate | `pytest tests/integration/test_debate_flow.py -v` |

## Restrições Técnicas Ativas
- Input do agente: ≤ 3000 chars (Truncamento: System > Issues > Defesa > Proposta > Decisões).
- Convergência: Jaccard > 0.7 ou 2 rounds sem novos issues.
- Spawn: ≥ 3 issues mesma categoria (Security, Scalability, etc).
