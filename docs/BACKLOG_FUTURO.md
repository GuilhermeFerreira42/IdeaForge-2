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
- **Status:** CONCLUÍDO

---

## Próximos Passos (Legacy Migration / Optimization) [PROPOSTA]

A Onda 3 conclui o MVP do IdeaForge 2 (Debate-Only). A partir daqui, as sugestões são de manutenção e expansão:

### Onda 4 — Refinamento e Performance (Opcional)
- **W4-01**: Cache de inferência para rounds idênticos.
- **W4-02**: Migração definitiva dos arquivos legados remanescentes em `idea-forge/src/`.
- **W4-03**: Interface Web (Gradio/Streamlit) para visualização do Board em tempo real.

---

## Regras do Backlog
1. Itens movem de `PENDENTE` para `CONCLUÍDO` apenas após validação com critério binário
2. A IA propõe o `CONTRATOS_DA_ONDA` — o usuário valida.