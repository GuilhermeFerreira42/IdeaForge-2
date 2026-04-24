# DECISION_LOG — IdeaForge 2

## Formato
`[FASE] | [TIPO] | [DECISÃO] | [MOTIVO] | [ARQUIVOS IMPACTADOS]`

Tipos: ADD, MOD, DEL, FREEZE, RULE, CFG, FIX

---

### Fase 0 — Planejamento e Arquitetura do IdeaForge 2

F0 | RULE | Branch `v2-debate-only` no repo existente, não repo novo | Preserva histórico git e ~1200 LOC de infraestrutura reutilizável | Todo o repositório
F0 | DEL | Remover todo código PRD-specific: SectionalGenerator, ProductManagerAgent, ConsistencyChecker, exemplars, context extractors, output validator, golden examples, architect agent, security reviewer, plan generator | Pipeline PRD colapsa em modelos pequenos; debate é o que funciona | ~12 arquivos em src/
F0 | RULE | Orquestrador 100% programático (zero LLM para decisões de fluxo) | Modelos pequenos decidem mal sobre meta-decisões; código é determinístico e testável | core/adaptive_orchestrator.py
F0 | CFG | MAX_ROUNDS=10, MAX_AGENTS=5, MIN_ROUNDS=2, MAX_EXPANSION_RETRIES=3 | Prevenir loops infinitos e explosão de complexidade | core/adaptive_orchestrator.py, config/settings.py
F0 | ADD | ValidationBoard com 3 categorias: Issues (OPEN→RESOLVED), Decisões (PROPOSED→VALIDATED), Pressupostos (UNTESTED→FLAGGED) | Tracker v1 só rastreava problemas; decisões e pressupostos são igualmente críticos | core/validation_board.py
F0 | RULE | Agentes nunca recebem transcript acumulado — apenas: ideia + estado do tracker + última resposta (~2000 chars) | Transcript cresce linearmente e sobrecarrega modelos pequenos | debate/debate_engine.py
F0 | ADD | Round 0: Proponent em modo expansão transforma ideia bruta em proposta estruturada de 7 seções | Debate sem substância inicial produz rounds desperdiçados | agents/proponent_agent.py
F0 | ADD | SynthesizerAgent (juíza neutra) recebe quadro de validações, não transcript completo | Dados estruturados são suficientes; transcript seria longo demais para modelo pequeno | agents/synthesizer_agent.py
F0 | ADD | Parser de 3 níveis: tabela → bullets → heurística com keywords | Modelos <3B não seguem formato de tabela; parser deve degradar graciosamente | debate/debate_state_tracker.py
F0 | ADD | ConvergenceDetector com Jaccard similarity + stopwords PT (threshold 0.7) | Detectar repetição de argumentos sem usar LLM; stopwords PT evitam falsos positivos | core/convergence_detector.py
F0 | ADD | Spawning de agentes de banco pré-definido, threshold ≥3 issues na mesma categoria | Agentes pré-definidos são testáveis; quando MAX_AGENTS atingido, spawn é bloqueado com warning | agents/specialist_profiles.py
F0 | ADD | Fallback do SynthesizerAgent: relatório mínimo direto do ValidationBoard | Único componente sem fallback; dump estruturado preserva 100% dos dados | core/report_generator.py
F0 | RULE | TDD rigoroso: testes antes do código, integração progressiva | Impede refatorações cascateadas e garante qualidade incremental | tests/
F0 | CFG | Modelo inicial de teste: gpt-oss:20b-cloud | 20B é onde o sistema v1 funciona bem; valida sem riscos de capacidade | config/settings.py
F0 | RULE | RF-006: critério de aceite medido via fixtures com issues conhecidos | Critério "≥80% de issues capturados" precisa de mecanismo programático, não subjetivo | tests/fixtures/
F0 | CFG | RNF-01: overhead de orquestração ≤500ms (excluindo inferência LLM) | Tempo total depende do hardware; overhead de código é o que controlamos | core/adaptive_orchestrator.py
F0 | DEL | Removidos 4 agents PRD-specific (architect, consistency_checker, product_manager, security_reviewer) | PRD-specific, sem uso no debate-only | src/agents/
F0 | DEL | Removidos 5 arquivos core PRD-specific + exemplars/ | NEXUS passes, extratores e validadores de PRD | src/core/
# DECISION_LOG — IdeaForge 2

## Formato
`[FASE] | [TIPO] | [DECISÃO] | [MOTIVO] | [ARQUIVOS IMPACTADOS]`

Tipos: ADD, MOD, DEL, FREEZE, RULE, CFG, FIX

---

### Fase 0 — Planejamento e Arquitetura do IdeaForge 2

F0 | RULE | Branch `v2-debate-only` no repo existente, não repo novo | Preserva histórico git e ~1200 LOC de infraestrutura reutilizável | Todo o repositório
F0 | DEL | Remover todo código PRD-specific: SectionalGenerator, ProductManagerAgent, ConsistencyChecker, exemplars, context extractors, output validator, golden examples, architect agent, security reviewer, plan generator | Pipeline PRD colapsa em modelos pequenos; debate é o que funciona | ~12 arquivos em src/
F0 | RULE | Orquestrador 100% programático (zero LLM para decisões de fluxo) | Modelos pequenos decidem mal sobre meta-decisões; código é determinístico e testável | core/adaptive_orchestrator.py
F0 | CFG | MAX_ROUNDS=10, MAX_AGENTS=5, MIN_ROUNDS=2, MAX_EXPANSION_RETRIES=3 | Prevenir loops infinitos e explosão de complexidade | core/adaptive_orchestrator.py, config/settings.py
F0 | ADD | ValidationBoard com 3 categorias: Issues (OPEN→RESOLVED), Decisões (PROPOSED→VALIDATED), Pressupostos (UNTESTED→FLAGGED) | Tracker v1 só rastreava problemas; decisões e pressupostos são igualmente críticos | core/validation_board.py
F0 | RULE | Agentes nunca recebem transcript acumulado — apenas: ideia + estado do tracker + última resposta (~2000 chars) | Transcript cresce linearmente e sobrecarrega modelos pequenos | debate/debate_engine.py
F0 | ADD | Round 0: Proponent em modo expansão transforma ideia bruta em proposta estruturada de 7 seções | Debate sem substância inicial produz rounds desperdiçados | agents/proponent_agent.py
F0 | ADD | SynthesizerAgent (juíza neutra) recebe quadro de validações, não transcript completo | Dados estruturados são suficientes; transcript seria longo demais para modelo pequeno | agents/synthesizer_agent.py
F0 | ADD | Parser de 3 níveis: tabela → bullets → heurística com keywords | Modelos <3B não seguem formato de tabela; parser deve degradar graciosamente | debate/debate_state_tracker.py
F0 | ADD | ConvergenceDetector com Jaccard similarity + stopwords PT (threshold 0.7) | Detectar repetição de argumentos sem usar LLM; stopwords PT evitam falsos positivos | core/convergence_detector.py
F0 | ADD | Spawning de agentes de banco pré-definido, threshold ≥3 issues na mesma categoria | Agentes pré-definidos são testáveis; quando MAX_AGENTS atingido, spawn é bloqueado com warning | agents/specialist_profiles.py
F0 | ADD | Fallback do SynthesizerAgent: relatório mínimo direto do ValidationBoard | Único componente sem fallback; dump estruturado preserva 100% dos dados | core/report_generator.py
F0 | RULE | TDD rigoroso: testes antes do código, integração progressiva | Impede refatorações cascateadas e garante qualidade incremental | tests/
F0 | CFG | Modelo inicial de teste: gpt-oss:20b-cloud | 20B é onde o sistema v1 funciona bem; valida sem riscos de capacidade | config/settings.py
F0 | RULE | RF-006: critério de aceite medido via fixtures com issues conhecidos | Critério "≥80% de issues capturados" precisa de mecanismo programático, não subjetivo | tests/fixtures/
F0 | CFG | RNF-01: overhead de orquestração ≤500ms (excluindo inferência LLM) | Tempo total depende do hardware; overhead de código é o que controlamos | core/adaptive_orchestrator.py
F0 | DEL | Removidos 4 agents PRD-specific (architect, consistency_checker, product_manager, security_reviewer) | PRD-specific, sem uso no debate-only | src/agents/
F0 | DEL | Removidos 5 arquivos core PRD-specific + exemplars/ | NEXUS passes, extratores e validadores de PRD | src/core/
F0 | DEL | Removida pasta planning/ (plan_generator.py) | Development Plan era PRD-specific | src/planning/
F0 | DEL | Removidos docs/archive/ e workflow/ | Histórico v1 fica no repo antigo; workflow embutido nos docs | docs/, workflow/
F0 | ADD | Criado tests/conftest.py com MockProvider | Base para TDD em todas as fases futuras | tests/

### Fase 1 — ValidationBoard + DebateStateTracker

F1 | ADD | ValidationBoard centraliza o estado do debate | Resolver mistura de responsabilidades do antigo tracker e persistir dados | core/validation_board.py
F1 | MOD | DebateStateTracker torna-se stateless e parser puro de Nível 1 a 3 | Permitir testes do parser sem mockar estado; suportar degradação graciosa com regex + heurística | debate/debate_state_tracker.py
F1 | FIX | _normalize_text() usa `unicodedata.normalize` para remover acentos antes de deduplicação | TDD apontou falha de equivalência ao deduplicar "Fálha" e "Falha" | debate/debate_state_tracker.py
F1 | ADD | register_assumptions_from_text() implementado antecipadamente | A API do Board precisará registrar Pressupostos na Fase 3 quando o Proponent começar a gerá-los | debate/debate_state_tracker.py
F1 | DEL | Toda manipulação de estado do Tracker mudou para chamar regras no Board | Tracker v1 acessava dicionários e misturava lógica de estado interno | debate/debate_state_tracker.py
F1 | ADD | ConvergenceDetector usando Similaridade Jaccard (bag-of-words) com stopwords PT | Evitar LLM_Overhead e detectar loops de saturação textual | core/convergence_detector.py
F1 | ADD | ConvergenceDetector rastreia Stale Rounds (saturação de issues) | Saturação pode ocorrer sem repetição textual exata; 2 rounds seguidos sem issues novos forçam parada | core/convergence_detector.py
F1 | ADD | AdaptiveOrchestrator com regras rígidas (MAX_ROUNDS, MIN_ROUNDS, SPAWN, CONVERGENCE) | Garantir que o Cérebro do sistema seja 100% determinístico e controlável | core/adaptive_orchestrator.py
F1 | RULE | Ordem de Avaliação no Orchestrator (STOP Force > CONTINUE Force > SPAWN > CONVERGE > CONTINUE) | Prevenir intersecções lógicas como tentar spawnar agentes num estado convergido | core/adaptive_orchestrator.py
