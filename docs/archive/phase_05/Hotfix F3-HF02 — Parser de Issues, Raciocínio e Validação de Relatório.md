**Mapa de causas-raiz identificadas no código:**

**Bug A — `_canonicalize_table()` usa `ISS-000` fixo para todos os issues** → o `_parse_level1` exige IDs únicos como `ISS-\d+`, mas todos chegam como `ISS-000`. O `_deduplicate()` rejeita o segundo issue em diante porque `ISS-000` já existe no board. Resultado: apenas 1 issue registrado em todo o debate.

**Bug B — `_parse_level1` exige 5 colunas mas tabela do Crítico tem 4** → o pattern `\|\s*(ISS-\d+)\s*\|\s*(HIGH|MED|LOW)\s*\|\s*(\w+)\s*\|\s*([^|]+)\|` após a canonicalização gera `| ISS-000 | SEV | CAT | DESC (Sugere-se: SUG) |` — 4 colunas sem coluna final de sugestão separada — mas o regex funciona. O problema real está no ponto A acima.

**Bug C — `StreamHandler` com `show_thinking=False` ainda exibe raciocínio** → quando o modelo usa campo `thinking` nativo (como `gpt-oss:20b-cloud`), `_render_thinking_chunk()` é chamado independentemente de `show_thinking`. A bifurcação `if self.show_thinking` existe mas só controla a renderização visual — o raciocínio ainda aparece porque `show_thinking` está sendo passado como `True` na instanciação (valor default), enquanto `think=False` controla apenas o payload da API.

**Bug D — `SynthesizerAgent._validate_report()` retorna lista parcial mas `ReportGenerator` aceita ≥3** → o modelo gerou relatório com apenas 3 das 5 seções obrigatórias (faltou `## Decisões Validadas` e `## Issues Pendentes`), mas `len(sections_present) < 3` não disparou o fallback. O threshold correto deveria ser 5.

---

# Hotfix F3-HF02 — Parser de Issues, Raciocínio e Validação de Relatório

> Natureza: Hotfix da Onda 3. Não cria onda nem fase nova.
> Causa-raiz: 4 bugs independentes em 4 arquivos.
> Arquivos de produção modificados: 4.
> Arquivos de teste modificados: 3.
> Escopo congelado: intocado.

---

## PARTE 1 — PROBLEMA E SOLUÇÃO

| ID | Arquivo | Bug | Impacto | Solução |
|---|---|---|---|---|
| BUG-A | `round_executor.py` | `_canonicalize_table()` atribui `ISS-000` fixo a todos os issues | Apenas 1 issue registrado em todo o debate; deduplicação rejeita todos os subsequentes | Gerar ID único por linha usando hash da descrição |
| BUG-B | `stream_handler.py` | `show_thinking=True` é o default; `think=False` na API não controla exibição visual | Raciocínio aparece mesmo quando usuário desativa pensamento profundo | `show_thinking` deve ser derivado de `think` no `Controller`; repassado ao `OllamaProvider` |
| BUG-C | `report_generator.py` | Threshold de fallback é `< 3 seções` em vez de `< 5` | Relatório com seções faltando é aceito como válido | Threshold corrigido para `< 5` |
| BUG-D | `synthesizer_agent.py` | Prompt não instrui o modelo a incluir conteúdo do debate nas seções | Board com dados válidos gera `(Nenhum registro)` porque o modelo interpreta a regra 1 de forma excessivamente restritiva | Adicionar instrução explícita: "O board contém os dados do debate — use-os" |

---

## PARTE 2 — ESPECIFICAÇÃO DAS CORREÇÕES

### 2.1 `src/debate/round_executor.py` — BUG-A

**Problema no código atual:**
```python
# Linha atual — ID fixo para todos os issues
new_lines.append(f"| ISS-000 | {sev} | {cat} | {desc_sug} |")
```

**Correção:**
```python
# Gerar ID único por linha baseado em hash da descrição + posição
import hashlib
unique_id = f"ISS-{abs(hash(cols[2][:50])) % 9000 + 1000}"
new_lines.append(f"| {unique_id} | {sev} | {cat} | {desc_sug} |")
```

**Por que isso resolve:** cada issue recebe um ID único. O `_deduplicate()` usa tanto `issue_id` quanto `normalized description` para deduplicar — IDs únicos eliminam a rejeição em cascata.

---

### 2.2 `src/core/stream_handler.py` — BUG-B

**Problema:** `show_thinking` controla a exibição visual, mas não está sendo passado corretamente pela cadeia `Controller → OllamaProvider → StreamHandler`. O `OllamaProvider` instancia `StreamHandler(show_thinking=self.show_thinking)`, mas `self.show_thinking` tem default `True` e o `Controller` não o repassa.

**Correção em `src/core/controller.py`:**
```python
def _get_provider(self, model_name: str, think: bool) -> OllamaProvider:
    return OllamaProvider(
        model_name=model_name,
        think=think,
        show_thinking=think  # ← show_thinking espelha think
    )
```

**Lógica:** se o usuário ativou `think=True`, quer ver o raciocínio → `show_thinking=True`. Se desativou `think=False`, não quer ver → `show_thinking=False`. São a mesma decisão do usuário.

**Nenhuma mudança no `stream_handler.py`** — a lógica já está correta lá. O bug era no ponto de instanciação.

---

### 2.3 `src/core/report_generator.py` — BUG-C

**Problema no código atual:**
```python
# Threshold errado — aceita relatório com 3 seções (faltam 2)
if synth_result["status"] == "error" or len(synth_result.get("sections_present", [])) < 3:
```

**Correção:**
```python
# Threshold correto — exige todas as 5 seções obrigatórias
REQUIRED_SECTION_COUNT = 5
if synth_result["status"] == "error" or len(synth_result.get("sections_present", [])) < REQUIRED_SECTION_COUNT:
```

---

### 2.4 `src/agents/synthesizer_agent.py` — BUG-D

**Problema no prompt atual:** a regra 1 ("Se não está no Board, não existe") está sendo interpretada pelo modelo como "se o board está vazio, escreva nenhum registro em tudo" — mesmo quando o board **tem** dados que o parser não capturou corretamente por causa do BUG-A.

Com o BUG-A corrigido, o board terá dados reais. Mas o prompt precisa de instrução explícita para que o modelo use esses dados ativamente nas seções.

**Adicionar ao prompt, após a regra 1:**
```
1. Se uma informação não está em BOARD_SNAPSHOT, ela NÃO existe — não a invente.
   ATENÇÃO: O BOARD_SNAPSHOT contém os dados reais do debate — issues encontrados,
   decisões tomadas e pressupostos identificados. USE esses dados para preencher
   as seções. Um board não-vazio NUNCA deve gerar "(Nenhum registro)" em Issues ou Decisões.
```

---

## PARTE 3 — SEQUÊNCIA DE IMPLEMENTAÇÃO (TDD)

### Passo 1 — `round_executor.py` (BUG-A — mais crítico)

**Testes a escrever/atualizar em `tests/unit/test_round_executor.py`:**
- `test_canonicalize_table_generates_unique_ids` — tabela com 3 linhas → 3 IDs diferentes
- `test_canonicalize_table_no_duplicate_iss000` — nenhum `ISS-000` presente no output
- `test_execute_critic_round_registers_multiple_issues` — MockProvider retorna tabela com 5 issues → board tem 5 issues

**Implementar** a correção do hash único.

**Critério de conclusão:** `pytest tests/unit/test_round_executor.py -v` → 100% PASS.

---

### Passo 2 — `controller.py` (BUG-B)

**Testes a atualizar em `tests/unit/test_controller.py`:**
- `test_controller_think_false_passes_show_thinking_false` — `think=False` → `OllamaProvider` instanciado com `show_thinking=False`
- `test_controller_think_true_passes_show_thinking_true` — `think=True` → `OllamaProvider` instanciado com `show_thinking=True`

**Implementar** `show_thinking=think` na instanciação do provider.

**Critério de conclusão:** `pytest tests/unit/test_controller.py -v` → 100% PASS.

---

### Passo 3 — `report_generator.py` (BUG-C)

**Testes a atualizar em `tests/unit/test_report_generator.py`:**
- `test_report_generator_fallback_when_4_sections` — Synthesizer retorna 4 seções → `fallback_used=True`
- `test_report_generator_fallback_when_3_sections` — Synthesizer retorna 3 seções → `fallback_used=True`
- `test_report_generator_success_requires_all_5_sections` — 5 seções → `fallback_used=False`

**Implementar** threshold `< 5`.

**Critério de conclusão:** `pytest tests/unit/test_report_generator.py -v` → 100% PASS.

---

### Passo 4 — `synthesizer_agent.py` (BUG-D)

**Testes a atualizar em `tests/unit/test_synthesizer_agent.py`:**
- `test_synthesizer_nonempty_board_fills_sections` — board com 3 issues → relatório não contém `(Nenhum registro)` em Issues Pendentes
- `test_synthesizer_prompt_contains_use_data_instruction` — prompt gerado contém a instrução de uso ativo dos dados

**Implementar** a instrução adicional no prompt.

**Critério de conclusão:** `pytest tests/unit/test_synthesizer_agent.py -v` → 100% PASS.

---

### Passo 5 — Validação integrada

```powershell
pytest tests/unit/test_round_executor.py tests/unit/test_controller.py tests/unit/test_report_generator.py tests/unit/test_synthesizer_agent.py -v
```

Todos devem passar. Depois executar manualmente com `gpt-oss:20b-cloud` e verificar:
- Múltiplos issues registrados no log
- Raciocínio não aparece quando `think=N`
- Relatório final tem as 5 seções preenchidas com dados reais

---

## PARTE 4 — ARQUIVOS MODIFICADOS

| Arquivo | Tipo de Mudança | Bug |
|---|---|---|
| `src/debate/round_executor.py` | Correção de lógica em `_canonicalize_table()` | BUG-A |
| `src/core/controller.py` | Adição de `show_thinking=think` em `_get_provider()` | BUG-B |
| `src/core/report_generator.py` | Threshold `< 3` → `< 5` | BUG-C |
| `src/agents/synthesizer_agent.py` | Instrução adicional no prompt | BUG-D |
| `tests/unit/test_round_executor.py` | Novos testes para IDs únicos | BUG-A |
| `tests/unit/test_controller.py` | Novos testes para `show_thinking` | BUG-B |
| `tests/unit/test_report_generator.py` | Testes para threshold correto | BUG-C |
| `tests/unit/test_synthesizer_agent.py` | Teste para board não-vazio | BUG-D |

**Congelados — não tocar:**

`src/debate/debate_engine.py`, `src/debate/context_builder.py`, `src/debate/debate_state_tracker.py`, `src/core/validation_board.py`, `src/core/adaptive_orchestrator.py`, `src/core/convergence_detector.py`, `src/agents/proponent_agent.py`, `src/agents/critic_agent.py`, `src/agents/specialist_profiles.py`

---

## PARTE 5 — ENTRADAS DO DECISION_LOG PÓS-IMPLEMENTAÇÃO

```
F3 | FIX | _canonicalize_table() gera ID único por hash em vez de ISS-000 fixo | Deduplicação rejeitava todos os issues após o primeiro | src/debate/round_executor.py
F3 | FIX | Controller passa show_thinking=think ao OllamaProvider | Raciocínio aparecia mesmo com think=False | src/core/controller.py
F3 | FIX | ReportGenerator threshold corrigido para < 5 seções obrigatórias | Relatório incompleto era aceito como válido | src/core/report_generator.py
F3 | FIX | SynthesizerAgent prompt instrui uso ativo dos dados do Board | Board não-vazio gerava (Nenhum registro) por interpretação excessivamente restritiva | src/agents/synthesizer_agent.py
```

---

**Critério binário de conclusão:**
`pytest tests/unit/test_round_executor.py tests/unit/test_controller.py tests/unit/test_report_generator.py tests/unit/test_synthesizer_agent.py -v` passa com 100%, e execução manual registra múltiplos issues no log com relatório final de 5 seções preenchidas.