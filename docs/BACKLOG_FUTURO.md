# BACKLOG ESTRATÉGICO — IdeaForge 2

## Intenção Original
- **Objetivo:** Sistema que recebe ideia bruta, executa debate adaptativo entre agentes e gera Relatório de Ideia Validada como contrato de interface para geração de PRD por modelo grande.
- **Estado Atual:** Onda 3 (Concluída) | 25/04/2026. Sistema completo com CLI e Síntese.
- **Meta Final:** Pipeline debate-only estável, testado com gpt-oss:20b-cloud, gerando relatórios que um modelo grande transforma em PRD completo.

---

## Onda 1 — Fundação e Core (Fases 1-2)
**Status:** CONCLUÍDO

## Onda 2 — Agentes e Debate (Fases 3-4)
**Status:** CONCLUÍDO

---

## Onda 3 — Síntese, Relatório e CLI (Fase 5)

| ID | Técnica/Feature | Descrição | Status |
|---|---|---|---|
| W3-01 | SynthesizerAgent | Juíza neutra que gera relatório Markdown | CONCLUÍDO |
| W3-02 | ReportGenerator | Persistência com fallback determinístico | CONCLUÍDO |
| W3-03 | Controller | Orquestrador Expansão -> Debate -> Síntese | CONCLUÍDO |
| W3-04 | CLI simplificada | Entry point com flags --idea, --model, --debug | CONCLUÍDO |
| W3-05 | Smoke test real | Execução completa com modelo real e validação | CONCLUÍDO |

### Meta da Onda 3
- **Critério binário:** `pytest tests/ -v` passa (unitários + integração) e relatório gerado preserva dados do board.
- **Status:** CONCLUÍDO (Incluindo Hotfixes HF01 e HF02)

---

## Onda 4 — Refinamento, Performance e Migração Legacy (Fase 6) [PROPOSTA]

A Onda 3 concluiu o MVP do IdeaForge 2 (Debate-Only). A Onda 4 foca em otimização de custos (cache), limpeza definitiva do legado e interface amigável.

### CONTRATOS_DA_ONDA 4 [PROPOSTA — aguardando validação do usuário]

| Contrato | Responsabilidade | Status |
| :--- | :--- | :--- |
| `src/core/cache_manager.py` | [NOVO] Cache de inferência persistente para evitar rounds redundantes | PENDENTE |
| `src/ui/dashboard.py` | [NOVO] Dashboard Gradio para visualização em tempo real do Board | PENDENTE |
| `idea-forge/src/` | [DELETE] Remoção completa do diretório legado após migração de utilitários | PENDENTE |

### Itens de Trabalho (Backlog Onda 4)
| ID | Técnica/Feature | Descrição | Status |
|---|---|---|---|
| W4-01 | Cache de inferência | Implementar cache baseado em hash de prompt para economizar tokens | PENDENTE |
| W4-02 | Migração Total | Mover utilitários remanescentes e deletar pasta `idea-forge/` | PENDENTE |
| W4-03 | Visual Dashboard | Criar interface visual para acompanhar o progresso dos agentes | PENDENTE |

---

## Regras do Backlog
1. Itens movem de `PENDENTE` para `CONCLUÍDO` apenas após validação com critério binário
2. A IA propõe o `CONTRATOS_DA_ONDA` — o usuário valida.