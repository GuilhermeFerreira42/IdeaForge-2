# DECISION_LOG — IdeaForge 2

## Formato
`[FASE] | [TIPO] | [DECISÃO] | [MOTIVO] | [ARQUIVOS IMPACTADOS]`

Tipos: ADD, MOD, DEL, FREEZE, RULE, CFG, FIX

---

### Fase 0 — Planejamento e Arquitetura do IdeaForge 2

F0 | RULE | Branch `v2-debate-only` no repo existente, não repo novo | Preserva histórico git e ~1200 LOC de infraestrutura reutilizável | Todo o repositório
F0 | DEL | Remover todo código PRD-specific | Pipeline PRD colapsa em modelos pequenos; debate é o que funciona | ~12 arquivos em src/
F0 | RULE | Orquestrador 100% programático (zero LLM para decisões de fluxo) | Modelos pequenos decidem mal sobre meta-decisões | core/adaptive_orchestrator.py
F0 | CFG | MAX_ROUNDS=10, MAX_AGENTS=5, MIN_ROUNDS=2, MAX_EXPANSION_RETRIES=3 | Prevenir loops infinitos e explosão de complexidade | config/settings.py
F0 | ADD | ValidationBoard com 3 categorias: Issues, Decisões, Pressupostos | Tracker v1 só rastreava problemas; decisões e pressupostos são críticos | core/validation_board.py
F0 | RULE | Agentes nunca recebem transcript acumulado (≤ 3000 chars total) | Transcript cresce linearmente e sobrecarrega modelos pequenos | debate/debate_engine.py
F0 | ADD | Round 0: Expansão transforma ideia bruta em proposta estruturada | Debate sem substância inicial produz rounds desperdiçados | agents/proponent_agent.py
F0 | ADD | SynthesizerAgent (juíza neutra) recebe quadro de validações | Dados estruturados são suficientes; transcript seria longo demais | agents/synthesizer_agent.py
F0 | ADD | Parser de 3 níveis: tabela → bullets → heurística | Modelos <3B não seguem formato de tabela; degradar graciosamente | debate/debate_state_tracker.py
F0 | ADD | ConvergenceDetector com Jaccard similarity + stopwords PT | Detectar repetição de argumentos sem usar LLM | core/convergence_detector.py
F0 | ADD | Fallback do SynthesizerAgent: dump direto do ValidationBoard | Único componente sem fallback; dump preserva 100% dos dados | core/report_generator.py
F0 | RULE | TDD rigoroso: testes antes do código | Impede refatorações cascateadas e garante qualidade incremental | tests/

### Fase 1 — ValidationBoard + DebateStateTracker

F1 | ADD | ValidationBoard centraliza o estado do debate | Resolver mistura de responsabilidades e persistir dados | core/validation_board.py
F1 | MOD | DebateStateTracker torna-se stateless | Permitir testes do parser sem mockar estado; suportar degradação graciosa | debate/debate_state_tracker.py
F1 | FIX | _normalize_text() usa normalization para remover acentos | TDD apontou falha de equivalência ao deduplicar "Fálha" e "Falha" | debate/debate_state_tracker.py
F1 | ADD | ConvergenceDetector usando Similaridade Jaccard (bag-of-words) | Evitar LLM_Overhead e detectar loops de saturação textual | core/convergence_detector.py
F1 | ADD | AdaptiveOrchestrator com regras rígidas | Garantir que o Cérebro do sistema seja 100% determinístico | core/adaptive_orchestrator.py

### Fase 2 — Agentes e Motor de Debate

F2 | ADD | prompt_templates.py centraliza diretivas e contratos | Garantir consistência nas instruções e facilitar manutenção | src/core/prompt_templates.py
F2 | ADD | RoundExecutor decompõe o loop do debate | Evitar God Class em DebateEngine; responsabilidade única | src/debate/round_executor.py
F2 | ADD | ContextBuilder com política de truncamento determinística | Evitar estouro de budget de prompt em modelos pequenos | src/debate/context_builder.py
F2 | ADD | Pipeline de Canonicalização (PT->EN e ID fake) | Suportar output real de LLM sem quebrar tracker legacy | src/debate/round_executor.py
F2 | ADD | ApplyDefensePatches com match fuzzy de seções | Permitir evolução contínua da proposta arquitetural | src/debate/round_executor.py
F2 | MOD | ProponentAgent refatorado para modos Expansão e Defesa | Implementar Round 0 produtivo e resposta direta a issues | src/agents/proponent_agent.py
F2 | FIX | DetectSubextraction mapeia resposta longa + 0 issues para falha | Evitar "falsa convergência" quando o modelo falha na tabela | src/debate/round_executor.py
F2 | MOD | DebateEngine integrado com fluxos de Round 0 e Spawn | Coordenar o pipeline completo de validação ponto a ponto | src/debate/debate_engine.py

### Fase 5 (Onda 3) — Síntese, Relatório e CLI

F5 | ADD | SynthesizerAgent (juíza técnica neutra) | Gerar relatório Markdown baseado apenas no ValidationBoard | src/agents/synthesizer_agent.py
F5 | ADD | ReportGenerator com fallback determinístico | Garantir entrega do relatório via dump se LLM falhar | src/core/report_generator.py
F5 | ADD | Controller orquestra Expansão -> Debate -> Síntese | Ponto único de entrada para coordenação do pipeline de alto nível | src/core/controller.py
F5 | ADD | CLI com argparse e modo debug | Interface robusta stdlib-only com visibilidade total do estado | src/cli/main.py
F5 | FIX | Corrigido nome de campo do transcript na integração do Controller | Alinhar com campo `transcript` real do DebateResult dataclass | src/core/controller.py
F5 | CFG | Restauração de OllamaProvider, CloudProvider e StreamHandler | Reabilitar execução real, streaming e telemetria v1 | src/models/, src/core/stream_handler.py
F5 | CFG | Adicionadas constantes de orquestração v2 em settings.py | Centralizar thresholds e limites de convergência do sistema | src/config/settings.py

### Hotfix F3-HF01 — Robustez e Seleção Interativa
F5 | FIX | OllamaProvider.generate() não mais engole erros — exceções tipadas propagam | Debate rodava com string de erro como resposta do LLM | src/models/ollama_provider.py
F5 | FIX | Controller._get_provider() corrigido: model_name= em vez de model= | TypeError ao instanciar OllamaProvider | src/core/controller.py
F5 | ADD | OllamaMemoryError e OllamaServiceError como exceções tipadas | Permitir tratamento diferenciado na CLI | src/models/ollama_provider.py
F5 | ADD | OllamaProvider.list_available_models() via GET /api/tags | Eliminar necessidade de o usuário saber o nome do modelo | src/models/ollama_provider.py
F5 | ADD | OllamaProvider.check_thinking_support() via subprocess ollama show | Substituir lista de keywords frágil por detecção real de capability | src/models/ollama_provider.py
F5 | MOD | Controller.run() exige model_name explícito — removido default silencioso | DEFAULT_MODEL="llama3" causava erro por modelo não instalado | src/core/controller.py
F5 | MOD | CLI reescrita com fluxo interativo: lista modelos -> verifica thinking -> coleta ideia | Experiência de uso sem necessidade de conhecer flags ou nomes de modelos | src/cli/main.py
F5 | RULE | OllamaMemoryError na CLI volta para seleção de modelo em vez de encerrar | Permitir que o usuário escolha modelo menor sem reiniciar o sistema | src/cli/main.py

### Hotfix F3-HF02 — Parser de Issues, Raciocínio e Validação de Relatório
F3 | FIX | _canonicalize_table() gera ID único por hash em vez de ISS-000 fixo | Deduplicação rejeitava todos os issues após o primeiro | src/debate/round_executor.py
F3 | FIX | Controller passa show_thinking=think ao OllamaProvider | Raciocínio aparecia mesmo com think=False | src/core/controller.py
F3 | FIX | ReportGenerator threshold corrigido para < 5 seções obrigatórias | Relatório incompleto era aceito como válido | src/core/report_generator.py
F3 | FIX | SynthesizerAgent prompt instrui uso ativo dos dados do Board | Board não-vazio gerava (Nenhum registro) por interpretação excessivamente restritiva | src/agents/synthesizer_agent.py

### Fase 6 (Onda 4) — Arquitetura Agnóstica a Domínios
F6 | ADD | DomainDetector e DomainContextBuilder (Round 0A) | Permitir detecção e montagem programática da "alma" de qualquer área | src/core/domain_detector.py
F6 | ADD | DomainProfile dataclass | Estrutura forte e estática das características do domínio a ser validado | src/core/domain_profile.py
F6 | ADD | DynamicPromptBuilder | Separar a estrutura do Motor/Debate da semântica inserindo variáveis dinâmicas | src/core/dynamic_prompt_builder.py
F6 | ADD | SpecialistFactory | Prover instâncias de agentes dinâmicos de acordo com a área do problema | src/agents/specialist_factory.py
F6 | ADD | CategoryNormalizer genérico e fallback `return clean` | Normalizar detecções do LLM para as dimensões canônicas, mitigando erros (NoneType) | src/core/category_normalizer.py
F6 | MOD | AdaptiveOrchestrator rastreia _spawned_categories (Deduplicação) | Prevenir que o debate repita o spawn do mesmo especialista infinitamente | src/core/adaptive_orchestrator.py
F6 | FIX | DebateStateTracker_parse_v4 ajusta regex e tabela fixa de saída | LLMs estavam perdendo colunas. Forçado formatação rígida de 4 colunas. | src/debate/debate_state_tracker.py
F6 | FIX | StreamHandler ganha buffer Unicode-safe (`safe_write`) | Modelos gpt-oss geravam símbolos Braille e hífen inquebrável, quebrando o CMD | src/core/stream_handler.py
