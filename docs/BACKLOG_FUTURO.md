# BACKLOG ESTRATÉGICO — IdeaForge 2

## Intenção Original
- **Objetivo:** Sistema que recebe ideia bruta, executa debate adaptativo entre agentes e gera Relatório de Ideia Validada como contrato de interface para geração de PRD por modelo grande.
- **Estado Atual:** Onda 4 (Concluída) | 26/04/2026. Sistema Agnóstico a Domínios com detecção programática.
- **Meta Final:** Pipeline debate-only estável, testado com gpt-oss:20b-cloud, escalável para qualquer domínio, gerando relatórios precisos.

---

## Onda 1 — Fundação e Core (Fases 1-2)
**Status:** CONCLUÍDO

## Onda 2 — Agentes e Debate (Fases 3-4)
**Status:** CONCLUÍDO

## Onda 3 — Síntese, Relatório e CLI (Fase 5)
**Status:** CONCLUÍDO

## Onda 4 — Arquitetura Agnóstica a Domínios (Fase 6)
**Status:** CONCLUÍDO

| ID | Técnica/Feature | Descrição | Status |
|---|---|---|---|
| W4-01 | Domain Profile & Context Builder | Detecção de domínio da ideia e injeção do perfil | CONCLUÍDO |
| W4-02 | Dynamic Prompt Builder | Separa a sintaxe rígida de comandos da semântica dos domínios | CONCLUÍDO |
| W4-03 | SpecialistFactory | Spawn on-the-fly de agentes especialistas sem hardcoding | CONCLUÍDO |
| W4-04 | Atualização Parser e Tracker | Tracker reestilizado com fail-safes para manter pipeline estável | CONCLUÍDO |

---

## Onda 5.0 — Qualidade Semântica e Convergência Real
**Status:** CONCLUÍDO

A execução de 26/04/2026 com a ideia "Agregador de Ofertas" revelou quatro falhas estruturais que invalidam o objetivo agnóstico da Onda 4. O BACKLOG da Onda 5 original (Cache, UI, Faxina Legada) foi **suspendido** para priorizar esses quatro bugs que contaminam todas as execuções futuras.

### Itens de Trabalho (Backlog Onda 5.0)
| ID | Técnica/Feature | Descrição | Status |
|---|---|---|---|
| W5Q-01 | JSON Resiliente | Caminho 3 (Boundary Detection) em `_extract_json()` e max_tokens 800 | CONCLUÍDO |
| W5Q-02 | Detector & Hybrid | Score Normalizado no DomainDetector e Fallback 'Hybrid' com 8 seções | CONCLUÍDO |
| W5Q-03 | Deduplicação Semântica | Threshold Jaccard 0.65 e ConvergenceDetector no AdaptiveOrchestrator | CONCLUÍDO |
| W5Q-04 | Synthesizer & Relatório | Snapshot da Juíza comprimido < 3200 chars e Resumo Executivo Padronizado | CONCLUÍDO |

---

## Onda 5.1 — Performance e Interface (Suspensa da Onda 5.0)
**Status:** PENDENTE

### Itens de Trabalho (Backlog Onda 5.1)
| ID | Técnica/Feature | Descrição | Status |
|---|---|---|---|
| W5-01 | Cache Semântico | Cachear prompts exatos limitando LLM requests | PENDENTE |
| W5-02 | UI em Tempo Real | Dashboard Gradio/Streamlit do ValidationBoard | PENDENTE |
| W5-03 | Faxina Legada | Identificar e remover `idea-forge/` após auditoria completa | PENDENTE |

**[PROPOSTA — aguardando validação do usuário]**
### CONTRATOS_DA_ONDA (5.1)
- **C1:** O Cache Semântico será implementado por interceptação das queries para o LLM via hash de inputs.
- **C2:** A UI utilizará Gradio (ou Streamlit) executada a partir de flag específica via CLI, consultando dados no disco, sem alterar o engine do debate sincrono.
- **C3:** A pasta legada `idea-forge/` será totalmente removida para limpar as importações que causaram conflitos no provider routing.

---

## Regras do Backlog
1. Itens movem de `PENDENTE` para `CONCLUÍDO` apenas após validação com critério binário
2. A IA propõe o `CONTRATOS_DA_ONDA` — o usuário valida.