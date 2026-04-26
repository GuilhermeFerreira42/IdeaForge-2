# Hotfix F3-HF01 — Seleção Interativa de Modelo e Tratamento de Erros do Ollama

> Natureza: Hotfix da Onda 3. Não cria onda nova.
> Arquivos de produção modificados: 3. Arquivos de teste modificados: 2.
> Escopo congelado: intocado.

---

## PARTE 1 — PROBLEMA E SOLUÇÃO

| Problema | Impacto Atual | Como Este Hotfix Resolve |
|---|---|---|
| `_get_provider()` passa `model=` em vez de `model_name=` | `TypeError` imediato ao iniciar | Corrigir o argumento na chamada |
| Ollama retorna JSON de erro (`{"error":"..."}`) mas o HTTP status não é sempre 4xx | Provider engole o erro, debate roda com string de erro como resposta do LLM | Inspecionar corpo da resposta antes de processar o stream |
| Erro de memória insuficiente encerra o sistema | Usuário perde o trabalho e precisa reiniciar manualmente | Exceção tipada `OllamaMemoryError` → CLI volta para seleção de modelo |
| Usuário precisa saber o nome exato do modelo de antemão | Uso impossível sem leitura prévia de documentação | CLI lista modelos disponíveis via `GET /api/tags` antes de executar |
| Sistema não sabe se modelo suporta `thinking` | `think=True` enviado para modelos que não suportam causa comportamento indefinido | `ollama show <modelo>` via subprocess detecta capability antes de perguntar |
| Flag `--idea` obrigatória impede uso interativo | Usuário tem que montar o comando na mão | Fluxo interativo padrão; `--idea` vira opcional para automação |

---

## PARTE 2 — ARQUITETURA DOS TRÊS ARQUIVOS

### 2.1 `src/models/ollama_provider.py` — Mudanças

**Novo: exceção tipada**
```python
class OllamaMemoryError(Exception):
    """Disparada quando o Ollama rejeita o modelo por memória insuficiente."""
    pass

class OllamaServiceError(Exception):
    """Disparada quando o Ollama está offline ou inacessível."""
    pass
```

**Novo: `list_available_models()` — método estático**
- Chama `GET http://localhost:11434/api/tags`
- Retorna `list[dict]` com `name` e `size` de cada modelo
- Lança `OllamaServiceError` se Ollama estiver offline

**Novo: `check_thinking_support(model_name)` — método estático**
- Executa `subprocess.run(["ollama", "show", model_name], capture_output=True, text=True)`
- Parseia o stdout procurando a linha `thinking` dentro da seção `Capabilities`
- Retorna `bool`

**Modificado: `generate_with_thinking()`**
- Após `response.raise_for_status()`, inspecionar o primeiro chunk do stream
- Se o chunk contiver `{"error":` → extrair a mensagem
- Se a mensagem contiver `"more system memory"` ou `"not enough memory"` → lançar `OllamaMemoryError`
- Qualquer outro erro do Ollama → lançar `OllamaServiceError`
- Remover o `except` que engolia erros silenciosamente — erros devem propagar

**Modificado: `_get_provider()` no Controller (bug fix)**
- `OllamaProvider(model=model)` → `OllamaProvider(model_name=model)`

---

### 2.2 `src/core/controller.py` — Mudanças

**Modificado: assinatura de `run()`**
```python
# Antes
def run(self, idea: str, model_override: str | None = None, debug: bool = False)

# Depois
def run(self, idea: str, model_name: str, think: bool = False, debug: bool = False)
```
`model_override` deixa de existir — o modelo agora é sempre fornecido explicitamente pela CLI após a seleção interativa. Não há mais default silencioso.

**Modificado: `_get_provider()`**
```python
def _get_provider(self, model_name: str, think: bool) -> OllamaProvider:
    return OllamaProvider(model_name=model_name, think=think)
```

**Novo: tratamento de `OllamaMemoryError` no `run()`**
```python
except OllamaMemoryError:
    return {"status": "memory_error", "error": "Memória insuficiente para este modelo"}
```
A CLI reconhece `status == "memory_error"` e volta para a seleção, em vez de encerrar.

---

### 2.3 `src/cli/main.py` — Reescrita do fluxo principal

O arquivo é **reescrito** — a lógica de `argparse` existente é substituída pelo fluxo interativo. `--debug` é mantida como flag opcional para uso avançado.

**Novo fluxo `main()`:**

```
LOOP externo (volta aqui se OllamaMemoryError):
  1. _display_header()
  2. models = OllamaProvider.list_available_models()
     → Se OllamaServiceError: exibir mensagem e sys.exit(1)
  3. model_name = _select_model(models)
     → Exibe lista numerada: "[1] qwen3.5:9b (6.6 GB)"
     → Usuário digita número
  4. think_supported = OllamaProvider.check_thinking_support(model_name)
     → Se True: perguntar "Ativar pensamento profundo? (s/N)"
     → Se False: think = False silenciosamente
  5. idea = _get_idea()
     → "Digite sua ideia: "
     → Se vazia: re-solicitar (máx 3x, depois sys.exit(1))
  6. result = controller.run(idea=idea, model_name=model_name, think=think, debug=debug)
  7. Se result["status"] == "memory_error":
     → Exibir aviso
     → Voltar ao início do LOOP (nova seleção de modelo)
  8. Se result["status"] == "success":
     → Exibir resumo e caminho do relatório
     → Encerrar normalmente
```

**Compatibilidade com automação (`--idea` opcional)**
A flag `--idea` continua existindo para uso não-interativo (scripts, CI). Se passada junto com `--model`, o fluxo interativo é pulado completamente. Se `--idea` for passada sem `--model`, o sistema ainda executa a seleção interativa de modelo.

---

## PARTE 3 — SEQUÊNCIA DE IMPLEMENTAÇÃO (TDD)

### Passo 1 — `OllamaProvider` (base de tudo)

**Testes a escrever primeiro em `tests/unit/test_ollama_provider.py`:**
- `test_list_models_returns_list` — mock de `requests.get` retornando JSON válido
- `test_list_models_raises_service_error_when_offline` — mock com `ConnectionError`
- `test_check_thinking_support_true` — mock de `subprocess.run` com output contendo `thinking`
- `test_check_thinking_support_false` — mock sem `thinking` no output
- `test_generate_raises_memory_error` — mock de response com `{"error":"more system memory..."}`
- `test_generate_raises_service_error_on_generic_ollama_error` — mock com erro genérico

**Depois implementar** as mudanças no arquivo de produção.

---

### Passo 2 — `Controller` (depende do Provider)

**Testes a atualizar em `tests/unit/test_controller.py`:**
- Atualizar assinatura: todos os testes que chamam `controller.run(idea=..., model_override=...)` passam a usar `controller.run(idea=..., model_name=..., think=...)`
- `test_controller_returns_memory_error_dict` — MockProvider que lança `OllamaMemoryError`

**Depois implementar** as mudanças no arquivo de produção.

---

### Passo 3 — `CLI` (depende de Controller e Provider)

**Testes a atualizar/escrever em `tests/unit/test_cli.py`:**
- `test_cli_interactive_flow_selects_model` — mock de `list_available_models` + `input()` simulado
- `test_cli_memory_error_loops_back` — mock retornando `memory_error` na primeira chamada, `success` na segunda; verificar que `list_available_models` foi chamado duas vezes
- `test_cli_idea_and_model_flags_skip_interactive` — `--idea "x" --model "y"` não chama `input()`
- `test_cli_service_error_exits` — `OllamaServiceError` → `sys.exit(1)`

**Depois implementar** a reescrita do arquivo de produção.

---

## PARTE 4 — DECISÕES ARQUITETURAIS

### ADR-HF01: Exceções Tipadas em vez de Retorno de String de Erro

| Campo | Valor |
|---|---|
| Status | ACEITA |
| Contexto | `OllamaProvider` engolia erros e retornava string de erro como conteúdo, corrompendo o debate silenciosamente |
| Decisão | Criar `OllamaMemoryError` e `OllamaServiceError`; remover o `except` que engolia |
| Alternativas Rejeitadas | Verificar string de erro no `Controller` — acoplamento de lógica de infra no orquestrador |
| Consequências | Erros propagam corretamente; comportamento silencioso eliminado |

### ADR-HF02: Modelo Sempre Explícito, Sem Default Silencioso

| Campo | Valor |
|---|---|
| Status | ACEITA |
| Contexto | `DEFAULT_MODEL = "llama3"` causava erro porque o modelo não estava instalado |
| Decisão | `Controller.run()` exige `model_name` explícito; CLI sempre fornece via seleção interativa |
| Alternativas Rejeitadas | Manter default e validar se existe — adiciona complexidade sem ganho real |
| Consequências | `settings.DEFAULT_MODEL` deixa de ser usado pelo Controller; pode ser removido futuramente |

### ADR-HF03: Detecção de `thinking` via `ollama show` em vez de Keywords

| Campo | Valor |
|---|---|
| Status | ACEITA |
| Contexto | Lista `REASONING_MODEL_KEYWORDS` não escala para modelos novos com nomes imprevisíveis |
| Decisão | `subprocess.run(["ollama", "show", model_name])` + parse de `Capabilities` |
| Alternativas Rejeitadas | Manter lista de keywords — frágil, requer manutenção manual a cada novo modelo |
| Consequências | `REASONING_MODEL_KEYWORDS` no `ollama_provider.py` pode ser removida; `ollama` precisa estar no PATH |

---

## PARTE 5 — ARQUIVOS MODIFICADOS E CONGELADOS

| Arquivo | Ação | Motivo |
|---|---|---|
| `src/models/ollama_provider.py` | MODIFICAR | Exceções tipadas, `list_available_models()`, `check_thinking_support()`, fix do `generate()` |
| `src/core/controller.py` | MODIFICAR | Nova assinatura de `run()`, tratamento de `OllamaMemoryError`, fix de `model_name=` |
| `src/cli/main.py` | REESCREVER | Fluxo interativo completo substituindo argparse puro |
| `tests/unit/test_ollama_provider.py` | CRIAR | Testes dos novos métodos estáticos e exceções |
| `tests/unit/test_controller.py` | ATUALIZAR | Adequar assinatura e adicionar teste de `memory_error` |
| `tests/unit/test_cli.py` | ATUALIZAR | Cobrir fluxo interativo e loop de retry |

**Congelados — não tocar:**

| Arquivo | Motivo |
|---|---|
| `src/debate/*` | Motor validado na Onda 2 |
| `src/core/validation_board.py` | Contrato imutável |
| `src/core/adaptive_orchestrator.py` | Lógica determinística validada |
| `src/agents/*` | Todos os agentes validados |
| `src/core/report_generator.py` | Fallback validado |
| `src/agents/synthesizer_agent.py` | Contrato imutável |

---

## PARTE 6 — ENTRADAS DO DECISION_LOG PÓS-IMPLEMENTAÇÃO

Após validação, adicionar ao `docs/DECISION_LOG.md`:

```
F3 | FIX | OllamaProvider.generate() não mais engole erros — exceções tipadas propagam | Debate rodava com string de erro como resposta do LLM | src/models/ollama_provider.py
F3 | FIX | Controller._get_provider() corrigido: model_name= em vez de model= | TypeError ao instanciar OllamaProvider | src/core/controller.py
F3 | ADD | OllamaMemoryError e OllamaServiceError como exceções tipadas | Permitir tratamento diferenciado na CLI | src/models/ollama_provider.py
F3 | ADD | OllamaProvider.list_available_models() via GET /api/tags | Eliminar necessidade de o usuário saber o nome do modelo | src/models/ollama_provider.py
F3 | ADD | OllamaProvider.check_thinking_support() via subprocess ollama show | Substituir lista de keywords frágil por detecção real de capability | src/models/ollama_provider.py
F3 | MOD | Controller.run() exige model_name explícito — removido default silencioso | DEFAULT_MODEL="llama3" causava erro por modelo não instalado | src/core/controller.py
F3 | MOD | CLI reescrita com fluxo interativo: lista modelos → verifica thinking → coleta ideia | Experiência de uso sem necessidade de conhecer flags ou nomes de modelos | src/cli/main.py
F3 | RULE | OllamaMemoryError na CLI volta para seleção de modelo em vez de encerrar | Permitir que o usuário escolha modelo menor sem reiniciar o sistema | src/cli/main.py
```

---

**Critério binário de conclusão do hotfix:**
`pytest tests/unit/test_ollama_provider.py tests/unit/test_controller.py tests/unit/test_cli.py -v` passa com 100%, e `python -m src.cli.main` exibe a lista de modelos instalados sem nenhuma flag adicional.