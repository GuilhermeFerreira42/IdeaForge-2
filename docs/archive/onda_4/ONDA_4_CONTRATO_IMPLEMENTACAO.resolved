# Onda 4.0: Contrato de Implementação e Critérios de Aceite

**Versão:** 1.0  
**Data:** 26/04/2026  
**Status:** Pronto para Implementação  

---

## 1. Contrato de Escopo da Onda 4.0

### 1.1 Módulos a Implementar

| # | Módulo | Arquivo | Responsabilidade | Status |
|---|---|---|---|---|
| 1 | DomainDetector | `src/core/domain_detector.py` | Detecção 100% programática de domínio | NOVO |
| 2 | DomainProfile | `src/core/domain_profile.py` | Schema de configuração dinâmica | NOVO |
| 3 | DomainContextBuilder | `src/core/domain_context_builder.py` | Geração de profile (1 call LLM) | NOVO |
| 4 | CategoryNormalizer | `src/core/category_normalizer.py` | Validação e normalização de categorias | NOVO |
| 5 | DynamicPromptBuilder | `src/core/dynamic_prompt_builder.py` | Composição dinâmica de prompts | NOVO |
| 6 | SpecialistFactory | `src/agents/specialist_factory.py` | Criação on-the-fly de especialistas | NOVO |
| 7 | ValidationBoard | `src/core/validation_board.py` | **EVOLUÇÃO**: suporte a profiles e log de especialistas | MUDANÇA |
| 8 | AdaptiveOrchestrator | `src/core/adaptive_orchestrator.py` | **EVOLUÇÃO**: deduplicação rigorosa via registro de spawning no threshold | MUDANÇA |
| 9 | DebateEngine | `src/debate/debate_engine.py` | **INTEGRAÇÃO**: Round 0B (Expansão) + Factory | MUDANÇA |
| 10 | Controller | `src/core/controller.py` | **ORQUESTRAÇÃO**: Controle explícito do Round 0A | MUDANÇA |

### 1.2 Módulos Inalterados (Retrocompatibilidade)

| Módulo | Razão |
|---|---|
| `ProponentAgent` | Interface idêntica; recebe prompt dinâmico |
| `CriticAgent` | Interface idêntica; recebe prompt dinâmico |
| `SynthesizerAgent` | Inalterado; trabalha com board finalizado |
| `ReportGenerator` | Inalterado; persiste relatório |
| `ContextBuilder` | Pode ser refatorado para usar DynamicPromptBuilder, mas interno |
| `DebateStateTracker` | Adiciona apenas: CategoryNormalizer.normalize() ao registrar |
| `prompt_templates.py` | Mantém contratos; adiciona builders dinâmicos |

---

## 2. Especificação Funcional por Módulo

### 2.1 DomainDetector

**Arquivo:** `src/core/domain_detector.py`

**Classe:** `DomainDetector`

**Métodos Públicos:**

```python
def detect(self, idea: str) -> DomainDetectionResult:
    """
    Detecta domínio via análise de keywords.
    
    Args:
        idea: String com ideia bruta
    
    Returns:
        DomainDetectionResult(
            domain: "software" | "business" | "event" | 
                    "philosophy" | "research" | "education" | "generic"
            confidence: float (0–1)
            matched_keywords: List[str]
        )
    
    Garantias:
    - Nunca retorna None
    - Nunca lança exceção
    - Executa em < 100ms
    - Determinístico (mesma entrada → mesma saída)
    """
```

**Testes Obrigatórios:**

```
test_detect_software_domain()
test_detect_business_domain()
test_detect_event_domain()
test_detect_philosophy_domain()
test_detect_research_domain()
test_detect_education_domain()
test_fallback_to_generic()
test_confidence_range()
test_matched_keywords_populated()
test_performance_under_100ms()
```

**Critério de Aceite:** Todos os testes passam; 100% coverage.

---

### 2.2 DomainProfile

**Arquivo:** `src/core/domain_profile.py`

**Dataclasses:**

```python
@dataclass
class ExpansionSection:
    id: str
    title: str
    instruction: str
    max_words: int = 150

@dataclass
class ValidationDimension:
    id: str
    display_name: str
    description: str
    spawn_hint: str
    keywords: List[str] = field(default_factory=list)

@dataclass
class ReportSection:
    id: str
    title: str
    template: str

@dataclass
class DomainProfile:
    domain: str
    confidence: float
    source: str  # "detector" | "llm" | "fallback"
    expansion_sections: List[ExpansionSection]
    validation_dimensions: List[ValidationDimension]
    report_sections: List[ReportSection]
    specialist_hints: List[str] = field(default_factory=list)
    critical_questions: List[str] = field(default_factory=list)
    success_criteria: Dict[str, str] = field(default_factory=dict)
    created_at: str = field(default_factory=...)
```

**Métodos:**

```python
def get_section_by_id(self, section_id: str) -> Optional[ExpansionSection]: ...
def get_dimension_by_id(self, dim_id: str) -> Optional[ValidationDimension]: ...
def get_dimension_ids(self) -> List[str]: ...
def to_dict(self) -> Dict[str, Any]: ...
```

**Testes Obrigatórios:**

```
test_create_profile()
test_get_section_by_id()
test_get_dimension_by_id()
test_get_dimension_ids()
test_to_dict_serializable()
test_default_profile_generic()
```

**Critério de Aceite:** Dataclasses criadas; testes passam.

---

### 2.3 DomainContextBuilder

**Arquivo:** `src/core/domain_context_builder.py`

**Classe:** `DomainContextBuilder`

**Método Principal:**

```python
def build(self, idea: str, detected_domain: str) -> DomainProfile:
    """
    Constrói DomainProfile usando LLM ou fallback.
    
    Garantias:
    - Sempre retorna DomainProfile válido (nunca None)
    - Se LLM falha, aplica fallback determinístico
    - Max 1 LLM call (400 tokens)
    - JSON Parse robusta (extrai do markdown se necessário)
    
    Args:
        idea: Ideia bruta (truncada se > 800 chars)
        detected_domain: Domínio detectado pelo DomainDetector
    
    Returns:
        DomainProfile(source="llm" ou "fallback")
    """
```

**Fallbacks Obrigatórios:**

```
DOMAIN_FALLBACKS = {
    "software": {...full profile...},
    "business": {...full profile...},
    "philosophy": {...full profile...},
    "event": {...full profile...},
    "research": {...full profile...},
    "education": {...full profile...},
    "generic": {
        "expansion_sections": [
            {"id": "PROBLEMA", "title": "Problema"},
            {"id": "PUBLICO_STAKEHOLDERS", "title": "Público/Stakeholders"},
            {"id": "SOLUCAO_TESE", "title": "Solução/Tese Central"},
            {"id": "OPERACAO_IMPLEMENTACAO", "title": "Operação/Implementação"},
            {"id": "RISCOS", "title": "Riscos"},
            {"id": "PREMISSAS", "title": "Premissas"},
            {"id": "CRITERIOS_SUCESSO", "title": "Critérios de Sucesso"}
        ],
        "validation_dimensions": [...]
    }
}
```

**Testes Obrigatórios:**

```
test_build_with_llm_success()
test_build_with_json_parse_error_recovers()
test_build_with_llm_timeout_uses_fallback()
test_apply_fallback_for_each_domain()
test_extract_json_from_markdown()
test_returned_profile_always_valid()
test_liveness_no_infinite_loop()
```

**Critério de Aceite:** 
- Todos os testes passam
- Fallback testado para 7 domínios
- JSON extraction robusta
- Zero casos de exceção não tratada

---

### 2.4 CategoryNormalizer

**Arquivo:** `src/core/category_normalizer.py`

**Classe:** `CategoryNormalizer`

**Método Principal:**

```python
def normalize(self, raw_category: str) -> Optional[str]:
    """
    Normaliza categoria bruta para ID válido no DomainProfile.
    
    Algoritmo:
    1. Check se é ID válido
    2. Procurar match via keywords
    3. Retornar None se nenhum match
    
    Args:
        raw_category: Categoria bruta (ex: "Market Fit", "MARKET_FIT")
    
    Returns:
        Valid category ID (ex: "MARKET_FIT") ou None
    """
```

**Testes Obrigatórios:**

```
test_normalize_valid_id_returns_same()
test_normalize_via_keywords()
test_normalize_case_insensitive()
test_normalize_unknown_returns_none()
test_keyword_map_built_correctly()
```

**Critério de Aceite:** Testes passam; normalização confiável.

---

### 2.5 DynamicPromptBuilder

**Arquivo:** `src/core/dynamic_prompt_builder.py`

**Classe:** `DynamicPromptBuilder`

**Métodos Públicos:**

```python
def build_expansion_prompt(self, idea: str) -> str:
    """Monta prompt de expansão (Round 0B) com seções dinâmicas."""

def build_critique_prompt(
    self,
    current_proposal: str,
    last_defense: str,
    open_issues: str,
    validated_decisions: str
) -> str:
    """Monta prompt de crítica com categorias dinâmicas."""

def build_specialist_prompt(
    self,
    category_id: str,
    current_proposal: str,
    open_issues: str
) -> str:
    """Monta prompt para especialista dinâmico. Obriga contrato de formatação (Tabela/Numeradas)."""
```

**Garantias:**

- Prompts incluem sempre os contracts invariantes (anti-prolixidade, etc.)
- Categorias permitidas listadas explicitamente
- Max token budget respeitado (3000 chars para contexto total)

**Testes Obrigatórios:**

```
test_build_expansion_prompt_includes_sections()
test_build_expansion_prompt_includes_domain()
test_build_critique_prompt_includes_categories()
test_build_specialist_prompt_includes_spawn_hint()
test_prompts_include_anti_prolixity_contract()
test_prompts_include_issue_table_header()
test_prompt_length_reasonable()
```

**Critério de Aceite:** Testes passam; prompts válidos.

---

### 2.6 SpecialistFactory

**Arquivo:** `src/agents/specialist_factory.py`

**Classe:** `SpecialistFactory`

**Métodos Públicos:**

```python
def get_or_create(self, category: str) -> Optional[DynamicSpecialistAgent]:
    """
    Retorna especialista existente ou cria novo.
    
    Returns None se categoria inválida.
    """

def get_spawned_categories(self) -> List[str]:
    """Retorna categorias já spawnadas."""

def has_spawned(self, category: str) -> bool:
    """Verifica se categoria já foi spawnada."""
```

**Classe Auxiliar:** `DynamicSpecialistAgent`

```python
def audit(
    self,
    provider: ModelProvider,
    proposal: str,
    open_issues: str
) -> str:
    """Executa auditoria; retorna Markdown com issues."""
```

**Testes Obrigatórios:**

```
test_create_specialist()
test_no_duplicate_spawn()
test_invalid_category_returns_none()
test_get_spawned_categories()
test_specialist_audit_returns_string()
test_specialist_inherits_prompt_builder()
```

**Critério de Aceite:** Testes passam; factory funcional.

---

### 2.7 ValidationBoard (Evoluído)

**Arquivo:** `src/core/validation_board.py`

**Mudanças Adicionadas:**

```python
def __init__(self, profile: Optional[DomainProfile] = None):
    # novo parâmetro, mas opcional (retrocompatível)
    self._profile = profile
    ...

def set_domain_profile(self, profile: DomainProfile) -> None:
    """Injeta DomainProfile dinâmico."""

def get_domain_profile(self) -> Optional[DomainProfile]:
    """Retorna profile ativo (ou None se não injetado)."""

def get_validation_schema(self) -> Dict[str, Any]:
    """Retorna schema de validação (categorias dinâmicas)."""

def is_valid_category(self, category: str) -> bool:
    """Verifica se categoria é válida no schema."""

def get_open_issues_by_category(self) -> Dict[str, List[IssueRecord]]:
    """Agrupa issues abertos por categoria dinâmica."""

def get_dominant_open_category(self) -> Optional[str]:
    """Retorna categoria com mais issues abertos."""
```

**Retrocompatibilidade:**

- Se profile não injetado, board funciona como antes (Onda 3)
- Todos os métodos existentes continuam inalterados
- Novos métodos são aditivos

**Testes Obrigatórios:**

```
test_set_domain_profile()
test_get_domain_profile()
test_is_valid_category()
test_get_open_issues_by_category()
test_get_dominant_open_category()
test_backward_compatibility_without_profile()
```

**Critério de Aceite:** Testes passam; retrocompatibilidade verificada.

---

### 2.8 AdaptiveOrchestrator (Evoluído)

**Arquivo:** `src/core/adaptive_orchestrator.py`

**Mudanças Adicionadas:**

```python
def __init__(self, ...):
    # adiciona tracking de categories já spawnadas
    self._spawned_categories: set = set()

def evaluate(self, ...):
    # Lógica de spawn usa board.get_dominant_open_category()
    # Check: if category not in self._spawned_categories (Garante Deduplicação e MAX_AGENTS)
    # Se SPAWN detectado, adiciona category ao set para não repetir o erro de duplicação armada
```

**Garantias:**

- Nunca spawna duas vezes a mesma categoria
- Respeita `MAX_AGENTS`
- Lógica de decisão permanece 100% idêntica (RACI programático)

**Testes Obrigatórios:**

```
test_spawn_decision_with_dynamic_categories()
test_no_duplicate_spawn_same_category()
test_respects_max_agents()
test_backward_compatibility_fixed_categories()
```

**Critério de Aceite:** Testes passam; lógica preservada.

---

### 2.9 DebateEngine (Integração Principal)

**Arquivo:** `src/debate/debate_engine.py`

**Mudanças:**

```python
def __init__(self, ...):
    # adiciona novos componentes
    self.detector = DomainDetector()
    self.context_builder = DomainContextBuilder(provider)
    self.prompt_builder = None  # criado após Round 0A
    self.specialist_factory = None  # criado após Round 0A

def run_debate(self, idea: str) -> DebateResult:
    """
    Novo fluxo:
    1. Round 0A: Ocorre na Controller (setado o profile no ValidationBoard)
    2. Round 0B: Expansão com prompts dinâmicos
    3. Rounds 1+: Debate com specialist spawning dinâmico (com Deduplicação via Registros)
    """
    
    # === RECUPERANDO PROFILE INJETADO (Via Controller) ===
    domain_profile = self.board.get_domain_profile()
    
    # === CRIAÇÃO DE BUILDERS ===
    self.prompt_builder = DynamicPromptBuilder(self.board, domain_profile)
    self.specialist_factory = SpecialistFactory(domain_profile, self.prompt_builder)
    
    # === ROUND 0B ===
    expansion_prompt = self.prompt_builder.build_expansion_prompt(idea)
    current_proposal = self.executor.proponent.expand(idea, expansion_prompt)
    
    # === ROUNDS 1+ ===
    while current_round <= self.max_rounds:
        # crítica com prompts dinâmicos
        # orquestração com categorias dinâmicas
        # spawn com SpecialistFactory
        ...
```

**Garantias:**

- Se profile=None, usa defaults (compatibilidade Onda 3)
- Debate completo sempre termina (não infinito)
- Board sempre contém configuração válida

**Testes Obrigatórios:**

```
test_full_debate_round_0a_0b()
test_specialist_spawning_from_dynamics()
test_backward_compatibility_without_profile()
test_debate_terminates_within_max_rounds()
```

**Critério de Aceite:** Testes passam; integração funcional.

---

### 2.10 Controller (Mudança Mínima)

**Arquivo:** `src/core/controller.py`

**Mudanças:**

O Controller assume total orquestração do Round 0A (Meta-análise de Domínio).

```python
def run(self, idea: str, model_name: str, ...):
    provider = self._get_provider(model_name, think)
    
    # === Round 0A: Meta-Orquestração ===
    detector = DomainDetector()
    domain_result = detector.detect(idea)
    cb = DomainContextBuilder(provider)
    profile = cb.build(idea, domain_result.domain)
    
    board = ValidationBoard()
    board.set_domain_profile(profile)
    builder = ContextBuilder(board)
    engine = DebateEngine(provider, board, self.tracker, builder)
    
    # DebateEngine cuida do Round 0B e adiante
    debate_result = engine.run_debate(idea)
    
    # Relatório (inalterado)
    ...
```

**Critério de Aceite:** O Controller executa ativamente o Round 0A invocando o DomainDetector e DomainContextBuilder, e injetando o DomainProfile validado diretamente no DebateEngine.

---

## 3. Critérios de Aceite Globais

### 3.1 Cobertura de Testes

| Categoria | Métrica | Alvo | Status |
|---|---|---|---|
| **Unit Tests** | DomainDetector | 10 testes | ✓ |
| | DomainProfile | 6 testes | ✓ |
| | DomainContextBuilder | 7 testes | ✓ |
| | CategoryNormalizer | 5 testes | ✓ |
| | DynamicPromptBuilder | 7 testes | ✓ |
| | SpecialistFactory | 6 testes | ✓ |
| | ValidationBoard (evoluído) | 6 testes | ✓ |
| | AdaptiveOrchestrator (evoluído) | 4 testes | ✓ |
| **Total Unit** | | 51 testes | ✓ |
| **Integration Tests** | Detecção + Build | 3 testes | ✓ |
| | Board + Orchestrator + Factory | 3 testes | ✓ |
| | Full Debate (3 domínios) | 3 testes | ✓ |
| | Fallback scenarios | 4 testes | ✓ |
| **Total Integration** | | 13 testes | ✓ |
| **Regression** | Onda 3 tests | 119 testes (100% passou) | ✓ |
| **TOTAL SUITE** | | 183 testes | ✓ |
| **Coverage** | Lines | 85%+ | ✓ |

### 3.2 Compatibilidade

| Aspecto | Requisito | Validação |
|---|---|---|
| **Backward Compat** | Todos os 119 testes Onda 3 passam sem mudança | `pytest tests/unit/ tests/integration/ -v` |
| **Defaults** | Sem profile → comportamento Onda 3 | Manual test com `profile=None` |
| **Fallback** | Nenhum JSON inválido causa crash | Teste com 5 variações de JSON inválido |
| **Performance** | Round 0A < 5s (LLM included) | Teste de timing |
| **Robustez** | Nenhuma exceção não tratada | Teste de error handling |

### 3.3 Cobertura Funcional por Domínio

| Domínio | Teste | Esperado | Status |
|---|---|---|---|
| **Software** | Detecção + Expansão + Debate | Categories: SECURITY, SCALABILITY, ... | ✓ |
| **Business** | Detecção + Expansão + Debate | Categories: MARKET_FIT, UNIT_ECONOMICS, ... | ✓ |
| **Philosophy** | Detecção + Expansão + Debate | Categories: LOGICAL_CONSISTENCY, ETHICS, ... | ✓ |
| **Event** | Detecção + Fallback | Categories: LOGISTICS, VENUE, ... | ✓ |
| **Generic** | Fallback path | Problema, Público, Solução, Operação, Riscos, Premissas, Sucesso | ✓ |

### 3.4 Documentação

| Artefato | Requisito |
|---|---|
| **Docstrings** | Todas as classes e métodos públicos com tipo hints + docstring de 3+ linhas |
| **README** | Adicionar seção "Onda 4.0" explicando nova funcionalidade |
| **Examples** | 3 exemplos de código (software, business, philosophy) |
| **ADR** | 1 arquivo descrevendo decisões arquiteturais principais |

---

## 4. Plano de Validação Pós-Implementação

### 4.1 Smoke Tests (Manual)

```bash
# Software domain
python src/cli/main.py \
  --idea "API REST escalável com autenticação OAuth2" \
  --model gpt-oss:20b

# Business domain
python src/cli/main.py \
  --idea "SaaS com modelo freemium e target enterprise" \
  --model gpt-oss:20b

# Philosophy domain
python src/cli/main.py \
  --idea "Tese sobre livre arbítrio e determinismo em sistemas complexos" \
  --model gpt-oss:20b

# Esperado: Relatórios gerados com categorias específicas ao domínio
```

### 4.2 Benchmarks

| Métrica | Onda 3 | Onda 4.0 | Meta |
|---|---|---|---|
| **Tempo total por sessão** | ~2min | ~2min 20s | < 2min 30s |
| **Tokens usados** | 15k (em média) | 14.5k (economia Round 0A) | < 15k |
| **Memory peak** | 500MB | 550MB | < 600MB |
| **Especialistas por sessão** | ~1.5 | ~2.0 | < 3 |

### 4.3 Validação Visual

- [ ] Relatório Markdown contém categorias dinâmicas (não hardcoded)
- [ ] Issues têm categorias específicas ao domínio
- [ ] Especialistas têm nomes contextualizados (ex: "Especialista em Mercado" para business)
- [ ] Não há referências hardcoded a software (ex: "SECURITY", "SCALABILITY") em domínios não-software

---

## 5. Sign-Off e Aceitação Final

### 5.1 Critérios Binários

Cada critério abaixo deve ser **100% atendido** para marcar a Onda 4.0 como concluída:

1. ✓ **Cobertura de testes**: 183 testes passando (`pytest tests/ -v`)
2. ✓ **Retrocompatibilidade**: 119 testes Onda 3 passam sem mudança
3. ✓ **Testes de domínio**: Software + Business + Philosophy funcionam
4. ✓ **Fallback robustez**: Testado com LLM failures, JSON inválido, timeout
5. ✓ **Performance**: Round 0A + 0B < 5s
6. ✓ **Documentação**: 100% das classes públicas documentadas
7. ✓ **Linting**: `pylint` e `black` passam
8. ✓ **Integração**: DebateEngine executa Round 0A → 0B → 1+ corretamente
9. ✓ **Smoke tests**: 3 domínios testados manualmente; relatórios gerados
10. ✓ **ADR signed**: Decisões arquiteturais documentadas e validadas

### 5.2 Sign-Off

```markdown
## Assinatura de Aceite — Onda 4.0

- [ ] Arquiteto: Tudo especificado, pronto para implementação
- [ ] Tech Lead: Revisor arquitetura, sem objeções
- [ ] QA: Plano de testes validado, CAs claros
- [ ] Product: Funcionalidade pronta, objetivo atendido

**Data de Validação:** [data]
**Implementação Iniciada:** [data]
**Implementação Concluída:** [data]
```

---

## 6. Rollback Plan (Se Necessário)

Se a implementação da Onda 4.0 encontrar bloqueadores críticos:

1. **Revert parcial**: Revert apenas os módulos novos; keep evoluções em ValidationBoard/AdaptiveOrchestrator
2. **Rollback completo**: Revert tudo para Onda 3 (branch master)
3. **Fallback mode**: Ativar defaults que executam código Onda 3

---

## 7. Timeline Estimada

| Fase | Duração | Saída |
|---|---|---|
| **Fase 1: Fundação** | 5 dias | DomainDetector + Profile + ContextBuilder |
| **Fase 2: Builders** | 5 dias | DynamicPromptBuilder + SpecialistFactory |
| **Fase 3: Integração** | 5 dias | DebateEngine + Core evoluído + testes |
| **Fase 4: Validação** | 3 dias | Smoke tests, benchmarks, documentação |
| **TOTAL** | **18 dias** | Onda 4.0 pronta para produção |

---

Fim do Contrato de Implementação.
