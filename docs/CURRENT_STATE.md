# CURRENT_STATE — IdeaForge 2
> Onda 4 concluída | Arquitetura Agnóstica a Domínios | 26/04/2026

## Arquitetura Ativa
- **Padrão:** Blackboard + Orquestrador Adaptativo + Fábrica de Especialistas Dinâmica.
- **Pipeline implementado:** Round 0A (Detecção de Domínio) → Round 0 (Expansão) → Debate Adaptativo Específico do Domínio (N rounds) → Síntese Baseada no Perfil → Relatório Markdown.
- **Código ativo:** `src/` (NÃO `idea-forge/src/`, que é legado v1 congelado).
- **LLM:** Ollama local via HTTP (`OllamaProvider`) integrado sem mocks. Suporta emojis/caracteres unicode de forma segura (`safe_write`).

| Fase | Onda | Foco | Status |
| :--- | :--- | :--- | :--- |
| Fase 6 | Onda 4 | Arquitetura Agnóstica (DomainProfile, DynamicPromptBuilder) | ✅ Concluída |

**Estado**: Produção Agnóstica Robusta (Detecção e spawn on-the-fly functional)

---

## 🛠️ Módulos Ativos (IdeaForge 2)

| Módulo | Caminho | Status |
| :--- | :--- | :--- |
| CLI / Entry Point | `src/cli/main.py` | ✅ Operacional (Tratamento Unicode Ok) |
| Controller | `src/core/controller.py` | ✅ Orquestra Round 0A |
| Domain Detector & Profile | `src/core/domain_*.py` | ✅ Implementado |
| Debate Engine | `src/debate/debate_engine.py` | ✅ Agnóstico |
| Validation Board | `src/core/validation_board.py` | ✅ Tipagem dinâmica |
| DynamicPromptBuilder | `src/core/dynamic_prompt_builder.py`| ✅ Injeção de contratos |
| SpecialistFactory | `src/agents/specialist_factory.py`| ✅ Spawn e deduplicação |
| CategoryNormalizer | `src/core/category_normalizer.py`| ✅ Mapping e Fallback genérico |
| Synthesizer Agent | `src/agents/synthesizer_agent.py` | ✅ Lê seções do profile |
| Stream Handler | `src/core/stream_handler.py` | ✅ Safe Write Resiliente |

---

## ✅ Cobertura de Testes
- **Total:** 144 testes
- **Status:** 100% Sucesso (Unitários + Integração)
- **Comando:** `pytest tests/unit/ tests/integration/ -v`
