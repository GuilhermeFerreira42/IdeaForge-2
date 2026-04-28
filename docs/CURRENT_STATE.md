# CURRENT_STATE — IdeaForge 2
> Onda 5.0 concluída | Qualidade Semântica e Convergência Real | 27/04/2026

## Arquitetura Ativa
- **Padrão:** Blackboard + Orquestrador Adaptativo + Fábrica de Especialistas Dinâmica.
- **Pipeline implementado:** Round 0A (Detecção de Domínio) → Round 0 (Expansão) → Debate Adaptativo (N rounds) → Síntese Baseada no Perfil → Relatório Markdown.
- **Código ativo:** `src/` (NÃO `idea-forge/src/`, que é legado v1 congelado).
- **LLM:** Ollama local via HTTP (`OllamaProvider`). Suporta modelos `-cloud` através do roteamento seguro, com fallback para o stub `CloudProvider` quando sem chave API. Guardas de integridade previnem a falsa convergência.

| Fase | Onda | Foco | Status |
| :--- | :--- | :--- | :--- |
| Fase 6.5 | Onda 5.0 | Qualidade Semântica, Prevenção de Falsa Convergência e Testes de Integração | ✅ Concluída |

**Estado**: Produção Estável e Blindada (Tolerância a falhas na API e deduplicação semântica)

---

## 🛠️ Módulos Ativos (IdeaForge 2)

| Módulo | Caminho | Status |
| :--- | :--- | :--- |
| CLI / Entry Point | `src/cli/main.py` | ✅ Operacional (Tratamento Unicode Ok) |
| Controller | `src/core/controller.py` | ✅ Roteamento de Providers Blindado |
| Domain Detector & Profile | `src/core/domain_*.py` | ✅ Densidade Semântica / Hybrid |
| Debate Engine & Tracker | `src/debate/` | ✅ Deduplicação Semântica Integrada |
| Round Executor | `src/debate/round_executor.py` | ✅ Guardas Anti-Falsa Convergência |
| Validation Board | `src/core/validation_board.py` | ✅ Tipagem dinâmica |
| DynamicPromptBuilder | `src/core/dynamic_prompt_builder.py`| ✅ Injeção de contratos |
| SpecialistFactory | `src/agents/specialist_factory.py`| ✅ Spawn e deduplicação |
| CategoryNormalizer | `src/core/category_normalizer.py`| ✅ Mapping e Fallback genérico |
| Synthesizer Agent | `src/agents/synthesizer_agent.py` | ✅ Lé seções do profile |
| Stream Handler | `src/core/stream_handler.py` | ✅ Safe Write Resiliente |

---

## ✅ Cobertura de Testes
- **Total:** 199 testes (42 testes de roteamento recém-adicionados)
- **Status:** 100% Sucesso (Unitários + Integração)
- **Comando:** `pytest tests/unit/ tests/integration/ -v`
