# Blueprint — Onda 3: Síntese, Relatório e CLI
**IdeaForge 2 | Fase 5 | 25/04/2026**
*Gerado via Protocolo NEXUS v1.1 — contexto: CURRENT_STATE.md + BACKLOG_FUTURO.md Onda 3 + DECISION_LOG F1/F2*

---

## PARTE 1 — VISÃO DA FASE

### 1.1 Identidade

| Atributo | Valor |
|---|---|
| Codinome | **VERDICT** |
| Fase | 5 (Onda 3, última) |
| Versão do Sistema | IdeaForge 2.0.0-beta |
| Declaração | Transformar o estado do debate em relatório legível e entregar pipeline completo por CLI. |

### 1.2 Problema e Solução

| Problema | Impacto | Como Esta Fase Resolve |
|---|---|---|
| Motor de debate produz `DebateResult` mas não há saída consumível | Usuário não consegue usar o output do debate sem código Python manual | `SynthesizerAgent` + `ReportGenerator` geram Markdown estruturado automaticamente |
| Pipeline não tem ponto de entrada para uso real | Sistema só funciona via testes; não há CLI | `src/cli/main.py` expõe `--idea`, `--interactive`, `--model`, `--debug` |
| SynthesizerAgent pode aluci­nar dados do debate | Relatório falso é pior que sem relatório | Regra: se dado não está no Board → não está no relatório; fallback é dump do Board |
| Falha do LLM na síntese interrompe o pipeline inteiro | Perda de todo o trabalho de debate executado | `ReportGenerator` tem fallback determinístico: dump completo do `ValidationBoard` |
| Não há teste de fumaça em condições reais | Aprovação em unitários não garante funcionamento ponta-a-ponta | `tests/smoke/` com 3 execuções consecutivas contra modelo real |

### 1.3 Escopo da Fase

**O QUE ESTÁ NO ESCOPO (W3-01 a W3-05):**
- ✅ `SynthesizerAgent` — juíza neutra, relatório 5 seções
- ✅ `ReportGenerator` — montagem final + fallback determinístico
- ✅ `Controller` — pipeline: Round 0 → Debate → Síntese → Persistência
- ✅ `src/cli/main.py` — entry point com 4 flags
- ✅ `tests/smoke/` — smoke test com modelo real

**O QUE NÃO ESTÁ NO ESCOPO:**
- ❌ Modificar qualquer arquivo de `src/debate/` (CONGELADO)
- ❌ Modificar `src/core/validation_board.py` (CONGELADO)
- ❌ Modificar `src/core/adaptive_orchestrator.py` (CONGELADO)
- ❌ Geração de PRD — sistema é debate-only
- ❌ Interface gráfica ou API HTTP
- ❌ Novo agente além do SynthesizerAgent

### 1.4 Princípios Arquiteturais da Fase

| Princípio | Descrição Concreta | Implicação Técnica |
|---|---|---|
| **Fidelidade ao Board** | SynthesizerAgent só pode referenciar dados presentes no `ValidationBoard.snapshot()` | Prompt proíbe explicitamente inferência; prompt inclui snapshot JSON completo |
| **Fallback Determinístico** | Falha do LLM na síntese nunca interrompe o pipeline | `ReportGenerator` detecta falha e executa `_fallback_dump()` sem LLM |
| **Orquestrador programático** | Controller não usa LLM para decisões de fluxo (invariante global) | Toda lógica de `Controller` é if/else Python puro |
| **CLI mínima** | Usuário executa o sistema em ≤3 comandos sem ler documentação | Flag `--idea "texto"` é suficiente; defaults cobrem o caso comum |
| **TDD estrito** | Testes escritos antes do código de produção (invariante global F0) | Sequência obrigatória: teste → FAIL → código → PASS |

---

## PARTE 2 — ARQUITETURA DE COMPONENTES

### 2.1 SynthesizerAgent

**Ficha Técnica**

| Atributo | Valor |
|---|---|
| ID interno | `W3-01` |
| Arquivo | `src/agents/synthesizer_agent.py` |
| Classe | `SynthesizerAgent` |
| Classe Base | nenhuma (standalone) |
| Dependências | `src/models/model_provider.py`, `src/core/validation_board.py` |
| Modo de Operação | Síncrono, stateless |
| Permissões | Leitura: `ValidationBoard.snapshot()`. Escrita: nenhuma. |

**Responsabilidade**
Receber o snapshot JSON do `ValidationBoard` ao final do debate, gerar via LLM um relatório Markdown de 5 seções obrigatórias, e retornar o texto do relatório. Proibido acessar transcript, histórico de rounds ou qualquer dado não presente no snapshot.

**Inputs**

| Input | Tipo | Descrição | Origem |
|---|---|---|---|
| `board` | `ValidationBoard` | Quadro de validações ao final do debate | `DebateEngine.run_debate()` |
| `idea_title` | `str` | Título/resumo da ideia debatida | `Controller` |
| `provider` | `ModelProvider` | Instância do provedor LLM configurado | `Controller` |

**Output**

```json
{
  "status": "success",
  "report_markdown": "# Relatório de Validação — IdeaForge\n\n## Sumário Executivo\n...\n## Decisões Validadas\n...\n## Issues Pendentes\n...\n## Matriz de Risco\n...\n## Veredito\n...",
  "sections_present": ["Sumário Executivo", "Decisões Validadas", "Issues Pendentes", "Matriz de Risco", "Veredito"],
  "source": "synthesizer"
}
```

**System Prompt do SynthesizerAgent**

```
Você é uma juíza técnica neutra. Sua única função é transformar os dados abaixo em um relatório estruturado.

REGRAS INVIOLÁVEIS:
1. Se uma informação não está em BOARD_SNAPSHOT, ela NÃO existe — não a invente.
2. Não expresse opinião pessoal. Registre apenas o que o debate produziu.
3. O relatório DEVE conter EXATAMENTE estas 5 seções, nesta ordem:
   - # Sumário Executivo
   - ## Decisões Validadas
   - ## Issues Pendentes
   - ## Matriz de Risco
   - ## Veredito
4. Se uma seção não tem dados, escreva: "(Nenhum registro nesta categoria)"
5. Responda APENAS com o relatório em Markdown. Nenhum texto antes ou depois.

IDEIA ANALISADA: {{IDEA_TITLE}}

BOARD_SNAPSHOT:
{{BOARD_SNAPSHOT_JSON}}
```

**Critério de Falha (aciona fallback)**
- `provider.generate()` lança exceção
- Resposta do LLM não contém pelo menos 3 das 5 seções obrigatórias
- Resposta está vazia ou é `None`

---

### 2.2 ReportGenerator

**Ficha Técnica**

| Atributo | Valor |
|---|---|
| ID interno | `W3-02` |
| Arquivo | `src/core/report_generator.py` |
| Classe | `ReportGenerator` |
| Classe Base | nenhuma |
| Dependências | `SynthesizerAgent`, `ValidationBoard` |
| Modo de Operação | Síncrono, stateless |
| Permissões | Leitura: `ValidationBoard.snapshot()`, `SynthesizerAgent.synthesize()`. Escrita: arquivo `.md` em disco. |

**Responsabilidade**
Receber o `ValidationBoard` e a instância do `SynthesizerAgent`, tentar síntese via LLM, detectar falha e acionar fallback determinístico se necessário, e persistir o relatório final em disco.

**Inputs**

| Input | Tipo | Descrição | Origem |
|---|---|---|---|
| `board` | `ValidationBoard` | Estado final do debate | `Controller` |
| `synthesizer` | `SynthesizerAgent` | Instância configurada | `Controller` |
| `idea_title` | `str` | Título da ideia | `Controller` |
| `output_path` | `str` | Caminho do arquivo de saída | `Controller` (via config) |

**Output (em disco)**

```
debate_RELATORIO_<timestamp>.md
```

**Output (retorno Python)**

```json
{
  "status": "success",
  "source": "synthesizer",
  "output_path": "debate_RELATORIO_20260425_151420.md",
  "fallback_used": false,
  "sections_present": ["Sumário Executivo", "Decisões Validadas", "Issues Pendentes", "Matriz de Risco", "Veredito"]
}
```

**Lógica de Fallback (`_fallback_dump`)**

Quando `synthesizer.synthesize()` falha ou retorna relatório inválido:

```
# Relatório de Validação — IdeaForge (Dump Automático)
> Gerado por fallback determinístico. O SynthesizerAgent falhou.

## Issues Registrados
[dump de todos os IssueRecord do Board]

## Decisões Registradas
[dump de todos os DecisionRecord do Board]

## Pressupostos Registrados
[dump de todos os AssumptionRecord do Board]

## Estatísticas
[Board.get_stats()]
```

Garantia: fallback preserva 100% dos dados do Board sem depender de LLM.

---

### 2.3 Controller

**Ficha Técnica**

| Atributo | Valor |
|---|---|
| ID interno | `W3-03` |
| Arquivo | `src/core/controller.py` |
| Classe | `Controller` |
| Classe Base | nenhuma |
| Dependências | `DebateEngine`, `ReportGenerator`, `SynthesizerAgent`, `ModelProvider`, `settings` |
| Modo de Operação | Síncrono, stateful (duração de 1 execução) |
| Permissões | Leitura: todos os módulos de `src/`. Escrita: disco via `ReportGenerator`. |

**Responsabilidade**
Receber ideia e configurações da CLI, instanciar os componentes, executar o pipeline `Round 0 → Debate Adaptativo → Síntese → Persistência`, e retornar o caminho do relatório gerado.

**Pipeline Completo**

```
1. Controller.run(idea, config)
   ├── Instanciar ModelProvider (Ollama ou Cloud)
   ├── Instanciar DebateEngine(provider)
   ├── debate_result = DebateEngine.run_debate(idea)
   ├── Instanciar SynthesizerAgent(provider)
   ├── Instanciar ReportGenerator()
   └── result = ReportGenerator.generate(board=debate_result.board,
                                          synthesizer=synthesizer,
                                          idea_title=idea,
                                          output_path=config.output_path)
```

**Output**

```json
{
  "status": "success",
  "output_path": "debate_RELATORIO_20260425_151420.md",
  "debate_rounds": 4,
  "issues_total": 7,
  "issues_resolved": 5,
  "fallback_used": false,
  "model_used": "gpt-oss:20b-cloud"
}
```

---

### 2.4 CLI (`src/cli/main.py`)

**Ficha Técnica**

| Atributo | Valor |
|---|---|
| ID interno | `W3-04` |
| Arquivo | `src/cli/main.py` |
| Framework | `argparse` (stdlib — zero dependências novas) |
| Dependências | `Controller`, `settings` |
| Modo de Operação | Síncrono, stateless |

**Flags**

| Flag | Tipo | Obrigatório | Default | Descrição |
|---|---|---|---|---|
| `--idea` | `str` | Sim (ou `--interactive`) | — | Ideia a ser validada (inline) |
| `--interactive` | `bool` (flag) | Não | `False` | Solicita ideia via prompt interativo |
| `--model` | `str` | Não | `settings.DEFAULT_MODEL` | Override do modelo LLM |
| `--debug` | `bool` (flag) | Não | `False` | Exibe transcript e board JSON no stderr |

**Validação de Entrada**
- `--idea` e `--interactive` são mutuamente exclusivos → erro com mensagem clara
- `--idea ""` (string vazia) → erro: "A ideia não pode ser vazia"
- Sem nenhuma das duas flags → mostrar `--help` e sair com código 1

**Saída Padrão (stdout)**

```
[IdeaForge 2] Iniciando validação...
[IdeaForge 2] Ideia: "Sistema de cache distribuído para APIs REST"
[IdeaForge 2] Modelo: gpt-oss:20b-cloud
[IdeaForge 2] Round 0: expandindo proposta...
[IdeaForge 2] Round 1/? em andamento...
[IdeaForge 2] Debate encerrado após 4 rounds (convergência detectada)
[IdeaForge 2] Sintetizando relatório...
[IdeaForge 2] Relatório salvo: debate_RELATORIO_20260425_151420.md
```

**Saída `--debug` (stderr)**

```
[DEBUG] Board JSON:
{...snapshot completo...}

[DEBUG] Transcript:
{...rounds completos...}
```

---

## PARTE 3 — FLUXO DE COMUNICAÇÃO

### 3.1 Diagrama de Sequência — Pipeline Completo

```mermaid
sequenceDiagram
    participant U as Usuário
    participant CLI as CLI (main.py)
    participant C as Controller
    participant DE as DebateEngine
    participant PA as ProponentAgent
    participant CA as CriticAgent
    participant AO as AdaptiveOrchestrator
    participant SA as SynthesizerAgent
    participant RG as ReportGenerator
    participant LLM as ModelProvider

    U->>CLI: python -m src.cli.main --idea "..."
    CLI->>C: Controller.run(idea, config)
    C->>DE: run_debate(idea)
    DE->>PA: expand(idea)
    PA->>LLM: generate(expansion_prompt)
    LLM-->>PA: proposta 7 seções
    PA-->>DE: ProposalResult

    loop Rounds Adaptativos
        DE->>CA: review(critique_prompt)
        CA->>LLM: generate(critique_prompt)
        LLM-->>CA: crítica com issues
        CA-->>DE: CritiqueResult
        DE->>AO: evaluate(round, current, previous, count)
        AO-->>DE: CONTINUE | STOP | SPAWN
        alt CONTINUE ou SPAWN
            DE->>PA: defend(defense_prompt)
            PA->>LLM: generate(defense_prompt)
            LLM-->>PA: defesa
            PA-->>DE: DefenseResult
        end
    end

    DE-->>C: DebateResult(board, rounds)
    C->>SA: synthesize(board, idea_title, provider)
    SA->>LLM: generate(synthesis_prompt)
    LLM-->>SA: relatório Markdown
    SA-->>C: SynthesisResult
    C->>RG: generate(board, synthesizer, idea_title, output_path)
    RG-->>C: ReportResult(output_path, fallback_used)
    C-->>CLI: ControllerResult
    CLI-->>U: output_path + resumo
```

### 3.2 Diagrama de Estado — Pipeline

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> EXPANDING: CLI recebe --idea
    EXPANDING --> DEBATING: Round 0 concluído
    DEBATING --> SYNTHESIZING: Orquestrador → STOP
    SYNTHESIZING --> SYNTHESIZER_OK: LLM retorna ≥3 seções válidas
    SYNTHESIZING --> SYNTHESIZER_FAIL: LLM falha ou retorna inválido
    SYNTHESIZER_OK --> PERSISTING: ReportGenerator.generate()
    SYNTHESIZER_FAIL --> PERSISTING: ReportGenerator._fallback_dump()
    PERSISTING --> DONE: Arquivo .md salvo em disco
    PERSISTING --> ERROR: IOError ao escrever arquivo
    DONE --> [*]
    ERROR --> [*]
    EXPANDING --> ERROR: ProponentAgent falha após MAX_EXPANSION_RETRIES
```

### 3.3 Tabela de Transições de Estado

| Estado Atual | Evento | Estado Novo | Condição | Ação |
|---|---|---|---|---|
| IDLE | `Controller.run()` chamado | EXPANDING | ideia não vazia | Instanciar componentes |
| EXPANDING | `ProponentAgent.expand()` retorna | DEBATING | proposta com ≥7 seções | Iniciar loop de debate |
| EXPANDING | `ProponentAgent.expand()` falha | ERROR | tentativas > MAX_EXPANSION_RETRIES | Logar erro, encerrar |
| DEBATING | `AdaptiveOrchestrator` → STOP | SYNTHESIZING | convergência ou MAX_ROUNDS | Entregar board ao Controller |
| SYNTHESIZING | LLM retorna relatório válido | SYNTHESIZER_OK | ≥3 seções presentes no texto | Passar para persistência |
| SYNTHESIZING | LLM falha ou retorna inválido | SYNTHESIZER_FAIL | exceção ou <3 seções | Logar warning, acionar fallback |
| SYNTHESIZER_OK | `ReportGenerator.generate()` salva | PERSISTING | — | Escrever arquivo em disco |
| SYNTHESIZER_FAIL | `ReportGenerator._fallback_dump()` | PERSISTING | — | Escrever dump do Board em disco |
| PERSISTING | Arquivo salvo com sucesso | DONE | sem IOError | Retornar `output_path` à CLI |
| PERSISTING | IOError ao escrever | ERROR | permissão negada ou disco cheio | Logar erro, retornar falha |

---

## PARTE 4 — SCHEMAS DE MENSAGENS

### 4.1 `DebateResult` (contrato entre DebateEngine → Controller)

```json
{
  "$schema": "debate_result_v2",
  "board": "<instância ValidationBoard>",
  "rounds_executed": 4,
  "final_proposal": "## 1. Problema\nCache distribuído...\n## 2. Solução\n...",
  "convergence_reason": "jaccard_threshold",
  "debate_transcript": [
    {
      "round": 1,
      "type": "critique",
      "agent": "CriticAgent",
      "content": "..."
    }
  ]
}
```

### 4.2 `SynthesisResult` (contrato entre SynthesizerAgent → ReportGenerator)

```json
{
  "status": "success",
  "report_markdown": "# Relatório de Validação...",
  "sections_present": ["Sumário Executivo", "Decisões Validadas", "Issues Pendentes", "Matriz de Risco", "Veredito"],
  "source": "synthesizer",
  "error": null
}
```

Em caso de falha:

```json
{
  "status": "error",
  "report_markdown": null,
  "sections_present": [],
  "source": "synthesizer",
  "error": "TimeoutError: LLM não respondeu em 60s"
}
```

### 4.3 `ReportResult` (contrato entre ReportGenerator → Controller)

```json
{
  "status": "success",
  "output_path": "debate_RELATORIO_20260425_151420.md",
  "fallback_used": false,
  "source": "synthesizer",
  "sections_present": ["Sumário Executivo", "Decisões Validadas", "Issues Pendentes", "Matriz de Risco", "Veredito"],
  "board_stats": {
    "issues_total": 7,
    "issues_resolved": 5,
    "decisions_validated": 3,
    "assumptions_flagged": 1
  }
}
```

---

## PARTE 5 — RECUPERAÇÃO DE ERROS

### 5.1 Classificação de Erros — Onda 3

| Nível | Tipo | Exemplos Concretos | Ação Automática | Timeout | Máx Tentativas |
|---|---|---|---|---|---|
| FATAL | IOError de persistência | Disco cheio, sem permissão de escrita | Log + retorno de erro para CLI | — | 1 |
| HIGH | Falha total do SynthesizerAgent | LLM offline, exceção não capturada | Acionar `_fallback_dump()` | 60s | 1 |
| MED | Relatório inválido do Synthesizer | <3 seções obrigatórias detectadas | Acionar `_fallback_dump()` | — | 0 (não retry) |
| LOW | Flag inválida na CLI | `--idea` e `--interactive` juntos | Print de erro + `sys.exit(1)` | — | 0 |
| INFO | Ideia vazia em `--interactive` | Usuário pressiona Enter sem digitar | Re-solicitar entrada (máx 3x) | — | 3 |

### 5.2 Fluxo de Self-Healing

```mermaid
flowchart TD
    A[SynthesizerAgent.synthesize()] --> B{Exceção?}
    B -->|Sim| C[Log WARNING: LLM falhou]
    B -->|Não| D{≥3 seções presentes?}
    D -->|Não| E[Log WARNING: relatório inválido]
    D -->|Sim| F[ReportResult status=success, source=synthesizer]
    C --> G[ReportGenerator._fallback_dump(board)]
    E --> G
    G --> H{IOError ao escrever?}
    H -->|Sim| I[Log CRITICAL: falha de persistência]
    H -->|Não| J[ReportResult status=success, source=fallback, fallback_used=True]
    I --> K[Retornar erro para CLI]
    F --> L[Escrever arquivo em disco]
    J --> L
    L --> M[Controller recebe output_path]
```

### 5.3 Padrão de Recuperação: Falha do SynthesizerAgent

- **DETECTOR:** `try/except Exception` em `ReportGenerator.generate()`
- **PATTERN:** Qualquer exceção de `synthesizer.synthesize()` OU `len(sections_present) < 3`
- **FLUXO:**
  1. Capturar exceção ou verificar contagem de seções
  2. Logar `WARNING: SynthesizerAgent falhou — acionando fallback`
  3. Chamar `self._fallback_dump(board, idea_title)`
  4. Montar `ReportResult` com `fallback_used=True`, `source="fallback"`
  5. Persistir normalmente

---

## PARTE 6 — REQUISITOS FUNCIONAIS E NÃO-FUNCIONAIS

### 6.1 Requisitos Funcionais

| ID | Requisito | Critério de Aceite | Prioridade | Complexidade |
|---|---|---|---|---|
| RF-W3-01 | SynthesizerAgent gera relatório com 5 seções obrigatórias | `sections_present` contém todas as 5 strings exatas | Must | Média |
| RF-W3-02 | SynthesizerAgent não inventa dados fora do Board | Teste com Board vazio: seções existem mas marcadas "(Nenhum registro)" | Must | Alta |
| RF-W3-03 | ReportGenerator aciona fallback quando LLM falha | Teste com MockProvider que lança exceção: `fallback_used=True` | Must | Média |
| RF-W3-04 | Fallback preserva 100% dos dados do Board | Issues + Decisions + Assumptions do Board presentes no dump | Must | Baixa |
| RF-W3-05 | Controller executa pipeline completo sem crash com MockProvider | `pytest tests/integration/test_controller_pipeline.py` passa | Must | Alta |
| RF-W3-06 | CLI aceita `--idea "texto"` e executa pipeline | Execução retorna `output_path` e arquivo existe em disco | Must | Baixa |
| RF-W3-07 | CLI `--interactive` solicita input via stdin | `input()` chamado uma vez, ideia passada ao Controller | Should | Baixa |
| RF-W3-08 | Flag `--debug` emite board JSON e transcript para stderr | stderr contém `"issues"` e `"rounds"` quando flag ativa | Should | Baixa |
| RF-W3-09 | `--idea` e `--interactive` são mutuamente exclusivos | CLI imprime erro e encerra com `sys.exit(1)` | Must | Baixa |
| RF-W3-10 | Smoke test: 3 execuções consecutivas sem crash | `pytest tests/smoke/ -v` passa 3x consecutivas com modelo real | Must | Alta |

### 6.2 Requisitos Não-Funcionais

| ID | Categoria | Requisito | Métrica | Target |
|---|---|---|---|---|
| RNF-W3-01 | Performance | Overhead do Controller (excluindo LLM) | Tempo de execução do código Python puro | ≤200ms |
| RNF-W3-02 | Performance | ReportGenerator persiste arquivo | Tempo de escrita em disco | ≤1s |
| RNF-W3-03 | Confiabilidade | Fallback sempre produz arquivo válido | Arquivo existe e tem tamanho > 0 bytes após falha do LLM | 100% |
| RNF-W3-04 | Usabilidade | Primeira execução com `--idea` | Número de comandos necessários | ≤3 |
| RNF-W3-05 | Observabilidade | Log estruturado em cada etapa do pipeline | Cada transição de estado tem entrada de log | 100% |
| RNF-W3-06 | Compatibilidade | CLI funciona em Python 3.10+ sem dependências novas | `argparse` é stdlib; zero pip installs adicionais | — |

### 6.3 Matriz de Rastreabilidade

| RF/RNF | Componente | Arquivo | Método/Função | Teste que Valida | Critério Binário |
|---|---|---|---|---|---|
| RF-W3-01 | SynthesizerAgent | `src/agents/synthesizer_agent.py` | `synthesize()` | `test_synthesizer_has_all_sections` | `len(result.sections_present) == 5` |
| RF-W3-02 | SynthesizerAgent | `src/agents/synthesizer_agent.py` | `synthesize()` | `test_synthesizer_empty_board_no_hallucination` | `"(Nenhum registro)" in report` |
| RF-W3-03 | ReportGenerator | `src/core/report_generator.py` | `generate()` | `test_report_generator_fallback_on_llm_error` | `result.fallback_used == True` |
| RF-W3-04 | ReportGenerator | `src/core/report_generator.py` | `_fallback_dump()` | `test_fallback_dump_preserves_all_records` | Todos os IDs do Board no dump |
| RF-W3-05 | Controller | `src/core/controller.py` | `run()` | `test_controller_pipeline_integration` | Sem exceção, `output_path` existe |
| RF-W3-06 | CLI | `src/cli/main.py` | `main()` | `test_cli_idea_flag_creates_report` | Arquivo existe após execução |
| RF-W3-07 | CLI | `src/cli/main.py` | `main()` | `test_cli_interactive_reads_stdin` | `input()` chamado |
| RF-W3-08 | CLI | `src/cli/main.py` | `main()` | `test_cli_debug_flag_emits_json` | stderr contém `"issues"` |
| RF-W3-09 | CLI | `src/cli/main.py` | `main()` | `test_cli_mutual_exclusion_exits` | `SystemExit` com código 1 |
| RF-W3-10 | Smoke | `tests/smoke/test_smoke.py` | `test_full_pipeline_smoke` | 3x `pytest tests/smoke/ -v` | Sem crash, arquivo gerado |
| RNF-W3-03 | ReportGenerator | `src/core/report_generator.py` | `_fallback_dump()` | `test_fallback_file_size_nonzero` | `os.path.getsize(path) > 0` |

---

## PARTE 7 — ÁRVORE DE ARQUIVOS E BLUEPRINT ESTRUTURAL

### 7.1 Arquivos Criados nesta Fase

```
src/
├── agents/
│   └── synthesizer_agent.py          ← NOVO (W3-01)
├── core/
│   ├── controller.py                  ← NOVO (W3-03)
│   └── report_generator.py           ← NOVO (W3-02)
└── cli/
    └── main.py                        ← NOVO (W3-04)

tests/
├── smoke/
│   ├── __init__.py                    ← NOVO
│   └── test_smoke.py                  ← NOVO (W3-05)
└── unit/
    ├── test_synthesizer_agent.py      ← NOVO
    ├── test_report_generator.py       ← NOVO
    ├── test_controller.py             ← NOVO
    └── test_cli.py                    ← NOVO
```

### 7.2 Arquivos CONGELADOS (não tocar)

```
src/debate/                            ← CONGELADO (Onda 2)
src/core/validation_board.py          ← CONGELADO
src/core/adaptive_orchestrator.py     ← CONGELADO
src/core/convergence_detector.py      ← CONGELADO
src/agents/proponent_agent.py         ← CONGELADO
src/agents/critic_agent.py            ← CONGELADO
src/agents/specialist_profiles.py     ← CONGELADO
```

### 7.3 Descrição por Arquivo

**`src/agents/synthesizer_agent.py`**
- **Propósito:** Juíza neutra que converte `ValidationBoard.snapshot()` em relatório Markdown de 5 seções via LLM.
- **Deps:** `src/models/model_provider.py`, `src/core/validation_board.py`
- **Interfaces públicas:**
  ```python
  def synthesize(board: ValidationBoard, idea_title: str, provider: ModelProvider) -> SynthesisResult
  def _build_prompt(board_snapshot: dict, idea_title: str) -> str
  def _validate_report(report: str) -> list[str]  # retorna seções encontradas
  ```

**`src/core/report_generator.py`**
- **Propósito:** Orquestra tentativa de síntese LLM + fallback determinístico e persiste arquivo em disco.
- **Deps:** `SynthesizerAgent`, `ValidationBoard`
- **Interfaces públicas:**
  ```python
  def generate(board: ValidationBoard, synthesizer: SynthesizerAgent, idea_title: str, output_path: str) -> ReportResult
  def _fallback_dump(board: ValidationBoard, idea_title: str) -> str
  def _persist(content: str, output_path: str) -> None
  ```

**`src/core/controller.py`**
- **Propósito:** Entry point do pipeline completo. Instancia componentes e executa: Debate → Síntese → Persistência.
- **Deps:** `DebateEngine`, `ReportGenerator`, `SynthesizerAgent`, `ModelProvider`, `settings`
- **Interfaces públicas:**
  ```python
  def run(idea: str, model_override: str | None = None, debug: bool = False) -> ControllerResult
  def _get_provider(model_override: str | None) -> ModelProvider
  def _get_output_path(idea_title: str) -> str
  ```

**`src/cli/main.py`**
- **Propósito:** Entry point CLI com argparse. Parse de flags, validação de entrada, delegação ao Controller.
- **Deps:** `Controller`, `settings`
- **Interfaces públicas:**
  ```python
  def main() -> None
  def _parse_args() -> argparse.Namespace
  def _get_idea(args: argparse.Namespace) -> str
  ```

---

## PARTE 8 — DECISÕES ARQUITETURAIS (ADRs)

### ADR-W3-01: Proibição de Inferência no SynthesizerAgent

| Campo | Valor |
|---|---|
| Status | ACEITA |
| Data | 25/04/2026 |
| Contexto | SynthesizerAgent recebe prompt com dados do Board; LLM pode "completar" dados não existentes |
| Decisão | Regra explícita no prompt: "Se não está no Board, não existe. Não invente." + seção vazia = "(Nenhum registro)" |
| Alternativas Rejeitadas | Pós-processamento para remover alucinações — impossível detectar programaticamente o que foi inventado |
| Consequências | Relatório pode ter seções com "(Nenhum registro)" — aceitável e correto |
| Mitigação | Teste específico `test_synthesizer_empty_board_no_hallucination` valida este comportamento |

### ADR-W3-02: Fallback Determinístico no ReportGenerator

| Campo | Valor |
|---|---|
| Status | ACEITA |
| Data | 25/04/2026 |
| Contexto | SynthesizerAgent é o único componente sem redundância; falha interromperia pipeline inteiro |
| Decisão | `_fallback_dump()` lê diretamente o Board e gera texto sem LLM |
| Alternativas Rejeitadas | Retry do SynthesizerAgent — se LLM falhou uma vez, provavelmente falhará de novo; adiciona latência sem ganho |
| Consequências | Relatório de fallback é menos rico (sem análise de risco elaborada), mas preserva 100% dos dados |
| Mitigação | Fallback marcado com header explícito: "Gerado por fallback determinístico" para auditabilidade |

### ADR-W3-03: argparse (stdlib) para CLI

| Campo | Valor |
|---|---|
| Status | ACEITA |
| Data | 25/04/2026 |
| Contexto | CLI precisa de flags `--idea`, `--interactive`, `--model`, `--debug` |
| Decisão | `argparse` da stdlib — zero dependências novas |
| Alternativas Rejeitadas | `click` — elegante mas adiciona dependência; `typer` — adiciona `click` + `typing_extensions`; sistema já é minimalista |
| Consequências | Sem auto-complete de shell; help menos formatado que click/typer |
| Mitigação | Aceitável para ferramenta interna de validação de ideias |

### ADR-W3-04: Detecção de Seções por String Exata

| Campo | Valor |
|---|---|
| Status | ACEITA |
| Data | 25/04/2026 |
| Contexto | `_validate_report()` precisa verificar se as 5 seções obrigatórias estão presentes |
| Decisão | `if "# Sumário Executivo" in report` — busca por string exata |
| Alternativas Rejeitadas | Regex — mais flexível mas aceita variações que o usuário não solicitou; viola determinismo |
| Consequências | LLM deve seguir o prompt exatamente; variação tipográfica causa fallback |
| Mitigação | Prompt instrui LLM com títulos exatos e exemplos |

### ADR-W3-05: Formato do Nome do Arquivo de Relatório

| Campo | Valor |
|---|---|
| Status | ACEITA |
| Data | 25/04/2026 |
| Contexto | Múltiplas execuções não devem sobrescrever relatórios anteriores |
| Decisão | `debate_RELATORIO_<YYYYMMDD_HHMMSS>.md` — timestamp no nome |
| Alternativas Rejeitadas | UUID — não legível por humanos; índice sequencial — requer estado persistido |
| Consequências | Nome previsível baseado em horário de execução |
| Mitigação | Padrão já usado no `.gitignore` (`debate_RELATORIO_*.md`) — consistência garantida |

### ADR-W3-06: Smoke Test em Diretório Separado

| Campo | Valor |
|---|---|
| Status | ACEITA |
| Data | 25/04/2026 |
| Contexto | Smoke tests usam modelo real (I/O de rede, latência alta, custo por token) |
| Decisão | `tests/smoke/` separado de `tests/integration/` e `tests/unit/`; não roda em `pytest tests/ -v` por padrão |
| Alternativas Rejeitadas | Marcador pytest `@pytest.mark.smoke` sem separação de diretório — mais difícil de excluir em CI |
| Consequências | Smoke tests rodam apenas quando `pytest tests/smoke/ -v` é explicitado |
| Mitigação | README e `.ai-context` documentam o comando separado |

---

## PARTE 9 — PLANO DE IMPLEMENTAÇÃO

### 9.1 Sequência de Implementação (TDD obrigatório)

**FASE 5.1 — SynthesizerAgent (W3-01)**

| # | Ação | Arquivo | Critério de Conclusão |
|---|---|---|---|
| 1 | Escrever `tests/unit/test_synthesizer_agent.py` | testes | Todos os testes existem e FALHAM |
| 2 | Implementar `src/agents/synthesizer_agent.py` | código | `pytest tests/unit/test_synthesizer_agent.py -v` → 100% PASS |

Testes obrigatórios:
- `test_synthesizer_has_all_sections` — relatório com 5 seções
- `test_synthesizer_empty_board_no_hallucination` — Board vazio → "(Nenhum registro)"
- `test_synthesizer_returns_error_on_llm_exception` — exceção do provider → `status="error"`
- `test_synthesizer_build_prompt_contains_snapshot` — snapshot JSON no prompt

---

**FASE 5.2 — ReportGenerator (W3-02)**

| # | Ação | Arquivo | Critério de Conclusão |
|---|---|---|---|
| 1 | Escrever `tests/unit/test_report_generator.py` | testes | Todos os testes existem e FALHAM |
| 2 | Implementar `src/core/report_generator.py` | código | `pytest tests/unit/test_report_generator.py -v` → 100% PASS |

Testes obrigatórios:
- `test_report_generator_success_path` — síntese OK → `fallback_used=False`
- `test_report_generator_fallback_on_llm_error` — exceção → `fallback_used=True`
- `test_report_generator_fallback_on_invalid_report` — <3 seções → fallback
- `test_fallback_dump_preserves_all_records` — todos os IDs do Board no dump
- `test_fallback_file_size_nonzero` — arquivo gerado tem tamanho > 0

---

**FASE 5.3 — Controller (W3-03)**

| # | Ação | Arquivo | Critério de Conclusão |
|---|---|---|---|
| 1 | Escrever `tests/unit/test_controller.py` | testes | Todos os testes existem e FALHAM |
| 2 | Implementar `src/core/controller.py` | código | `pytest tests/unit/test_controller.py -v` → 100% PASS |
| 3 | Escrever `tests/integration/test_controller_pipeline.py` | testes | Teste integração com MockProvider → PASS |

Testes unitários obrigatórios:
- `test_controller_run_returns_output_path` — resultado tem `output_path`
- `test_controller_debug_flag_emits_to_stderr` — `debug=True` → stderr não vazio
- `test_controller_model_override_passed_to_provider` — `model_override` repassado

Teste integração:
- `test_controller_pipeline_integration` — pipeline completo com MockProvider sem crash

---

**FASE 5.4 — CLI (W3-04)**

| # | Ação | Arquivo | Critério de Conclusão |
|---|---|---|---|
| 1 | Escrever `tests/unit/test_cli.py` | testes | Todos os testes existem e FALHAM |
| 2 | Implementar `src/cli/main.py` | código | `pytest tests/unit/test_cli.py -v` → 100% PASS |

Testes obrigatórios:
- `test_cli_idea_flag_creates_report` — `--idea "x"` → arquivo existe
- `test_cli_interactive_reads_stdin` — `--interactive` → `input()` chamado
- `test_cli_mutual_exclusion_exits` — `--idea` + `--interactive` → `SystemExit(1)`
- `test_cli_empty_idea_exits` — `--idea ""` → `SystemExit(1)`
- `test_cli_debug_flag_emits_json` — `--debug` → stderr contém `"issues"`

---

**FASE 5.5 — Smoke Test (W3-05)**

| # | Ação | Arquivo | Critério de Conclusão |
|---|---|---|---|
| 1 | Criar `tests/smoke/__init__.py` e `tests/smoke/test_smoke.py` | testes | — |
| 2 | Executar com modelo real | execução | 3x `pytest tests/smoke/ -v` sem crash, arquivo gerado e legível |

---

### 9.2 Critérios de Aceitação da Onda 3

```
DADO que o modelo real está disponível e configurado em settings
QUANDO o usuário executa: python -m src.cli.main --idea "Sistema de cache distribuído"
ENTÃO o sistema exibe progresso no stdout E um arquivo debate_RELATORIO_*.md é criado
  E o arquivo contém as seções: Sumário Executivo, Decisões Validadas, Issues Pendentes, Matriz de Risco, Veredito

DADO que o ModelProvider lança exceção durante a síntese
QUANDO ReportGenerator.generate() é chamado
ENTÃO fallback_used=True E arquivo gerado existe E tamanho > 0 bytes E contém todos os IDs do Board

DADO que --idea e --interactive são passados juntos
QUANDO a CLI é executada
ENTÃO sys.exit(1) É chamado E mensagem de erro é impressa no stderr

DADO que pytest tests/unit/ -v passa com 100%
E pytest tests/integration/ -v passa com 100%
QUANDO pytest tests/smoke/ -v é executado 3 vezes consecutivas
ENTÃO nenhuma exceção ocorre E relatório legível é gerado em cada execução
```

### 9.3 Métricas de Sucesso

| Métrica | Target | Como Medir |
|---|---|---|
| Cobertura de testes unitários | 100% dos métodos públicos | `pytest tests/unit/ --co -q \| wc -l` |
| Smoke test estabilidade | 3/3 execuções sem crash | `pytest tests/smoke/ -v` repetido 3x |
| Fallback confiabilidade | 100% | `test_report_generator_fallback_*` passa |
| Overhead Controller | ≤200ms | `time python -m src.cli.main --idea "x"` - tempo LLM |

---

## PARTE 10 — ESCOPO CONGELADO E BLINDAGEM

### 10.1 Arquivos Protegidos (exigem ADR para modificar)

| Arquivo | Motivo do Congelamento |
|---|---|
| `src/debate/*.py` | Motor validado na Onda 2; contrato `run_debate()` imutável |
| `src/core/validation_board.py` | Contrato `snapshot()`, `add_*`, `get_*_prompt()` imutável |
| `src/core/adaptive_orchestrator.py` | Lógica determinística validada; modificação requer revalidação completa |
| `src/agents/proponent_agent.py` | Contrato `expand()` e `defend()` imutável |
| `src/agents/critic_agent.py` | Contrato `review()` imutável |

### 10.2 Alterações Proibidas nesta Fase

- Modificar qualquer arquivo congelado (lista acima)
- Adicionar dependências externas além da stdlib
- Adicionar lógica de LLM ao Controller ou CLI
- Implementar endpoint HTTP ou interface gráfica
- Gerar PRD — sistema é debate-only

---

## PARTE 11 — ATUALIZAÇÃO DOS DOCS PÓS-FASE (ARCHIVING_PROTOCOL)

Após validação, executar `docs/ARCHIVING_PROTOCOL.md` com as seguintes atualizações:

**`docs/CURRENT_STATE.md`** — adicionar:
```
| SynthesizerAgent | src/agents/synthesizer_agent.py | synthesize(board, idea_title, provider) | F3 |
| ReportGenerator  | src/core/report_generator.py    | generate(), _fallback_dump()             | F3 |
| Controller       | src/core/controller.py          | run(idea, model_override, debug)         | F3 |
| CLI              | src/cli/main.py                 | main()                                   | F3 |
```

**`docs/BACKLOG_FUTURO.md`** — marcar W3-01 a W3-05 como `CONCLUÍDO` e Meta da Onda 3 como `CONCLUÍDO`.

**`docs/DECISION_LOG.md`** — adicionar entradas F3:
```
F3 | ADD | SynthesizerAgent com proibição de inferência via prompt | ...
F3 | ADD | ReportGenerator com fallback determinístico | ...
F3 | ADD | Controller como orquestrador do pipeline completo | ...
F3 | ADD | CLI com argparse (stdlib) | ...
F3 | FREEZE | src/debate/, validation_board.py, adaptive_orchestrator.py | Onda 3 validada |
```

**Mensagem de commit sugerida:**
```
feat(onda3): SynthesizerAgent + ReportGenerator + Controller + CLI

- W3-01: SynthesizerAgent — juíza neutra, 5 seções, sem alucinação
- W3-02: ReportGenerator — fallback determinístico via Board
- W3-03: Controller — pipeline Round0→Debate→Síntese→Persistência
- W3-04: CLI — argparse com --idea/--interactive/--model/--debug
- W3-05: Smoke test com modelo real (3 execuções consecutivas)

IdeaForge 2 — Onda 3 concluída. Pipeline debate-only completo.
```

---

## CLÁUSULA DE INTEGRIDADE

**Checklist de Completude**
- [x] Todo requisito tem ID único e critério de aceite verificável
- [x] Todo requisito tem teste na matriz de rastreabilidade
- [x] Toda decisão arquitetural tem ADR com alternativa rejeitada
- [x] Todo componente tem ficha técnica, inputs, outputs e exemplo JSON
- [x] Todo diagrama está em Mermaid renderizável
- [x] Todo schema de mensagem tem exemplo concreto preenchido
- [x] Todo cenário de falha tem estratégia de recuperação documentada
- [x] Contratos da Onda 3 confirmados usados como fatos (não questionados)
- [x] Escopo congelado explicitamente listado
- [x] Nenhuma seção contém "A DEFINIR" ou generalidades

**Declaração de Determinismo**
Este blueprint especifica exatamente 4 arquivos a criar em `src/`, 4 arquivos de teste unitário, 1 arquivo de integração e 1 diretório de smoke test. Cada arquivo tem interfaces públicas tipadas, contratos de input/output com exemplos JSON funcionais e testes que o validam. Uma IA executora pode implementar esta fase sem tomar nenhuma decisão arquitetural própria.