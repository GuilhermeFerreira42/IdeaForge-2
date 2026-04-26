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

## Onda 5 — Refinamento, Performance e Migração Legacy (Fase 7) [PROPOSTA]

A Onda 4 generalizou o MVP do IdeaForge 2 para funcionar em qualquer área de negócio. A Onda 5 foca na Otimização de Custos (Cache), Extinção de Legados e Interface Amigável (Visual UI).

### CONTRATOS_DA_ONDA 5 [PROPOSTA — aguardando validação do usuário]

| Contrato | Responsabilidade | Status |
| :--- | :--- | :--- |
| `src/core/cache_manager.py` | [NOVO] Cache de inferência persitente para evitar redundâncias e poupar LLM requests | PENDENTE |
| `src/ui/dashboard.py` | [NOVO] Micro-app Gradio ou Streamlit para visualização em tempo real do Debate/ValidationBoard | PENDENTE |
| `idea-forge/src/` | [DELETE] Remoção completa e segura da sub-pasta de código legado v1 após auditoria | PENDENTE |

### Itens de Trabalho (Backlog Onda 5)
| ID | Técnica/Feature | Descrição | Status |
|---|---|---|---|
| W5-01 | Cache Semântico | Cachear prompts exatos (e possivelmente near-matches) limitando repetições | PENDENTE |
| W5-02 | UI em Tempo Real | Dashboard para mostrar issues nascendo, resoluções, logs interativos do DebateEngine | PENDENTE |
| W5-03 | Faxina Legada | Identificar todo o repositório `/idea-forge/` e migrar configs restantes, depois `rm -rf` | PENDENTE |

---

## Regras do Backlog
1. Itens movem de `PENDENTE` para `CONCLUÍDO` apenas após validação com critério binário
2. A IA propõe o `CONTRATOS_DA_ONDA` — o usuário valida.