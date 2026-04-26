# Onda 4.0: Diagramas Arquiteturais e Matriz de Decisões

**Versão:** 1.0  
**Data:** 26/04/2026  
**Complemento ao:** Blueprint Definitivo — Onda 4.0

---

## 1. Diagramas Arquiteturais Detalhados

### 1.1 Arquitetura Geral de Componentes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      IdeaForge 2 — Onda 4.0                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐
│   CLI / Input   │
│  (main.py)      │
└────────┬────────┘
         │ idea: str
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  CONTROLLER (src/core/controller.py) — Round 0A: Meta-Orquestração      │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │ 1. Inicializa ModelProvider (Ollama ou Cloud)                  │   │
│  │ 2. DomainDetector.detect(idea) → DomainDetectionResult         │   │
│  │ 3. DomainContextBuilder.build() → DomainProfile                │   │
│  │ 4. Cria ValidationBoard() e injeta profile com schema dinâmico │   │
│  │ 5. Instancia DebateEngine com board PRÉ-CONFIGURADO            │   │
│  │ 6. Chama engine.run_debate(idea) → DebateResult                │   │
│  │ 7. Persiste relatório via ReportGenerator                      │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────┬──────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  DEBATE ENGINE — Round 0B+: Execução de Ciclos                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ Engine inicializa já recebendo o DomainProfile do Controller.  │    │
│  │ A lógica de DomainContext/Detector NÃO ocorre mais dentro do   │    │
│  │ Engine, mantendo sua responsabilidade focada em debater.       │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────┬──────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  DEBATE ENGINE — Round 0B: Expansão Contextualizada                     │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ DynamicPromptBuilder.build_expansion_prompt(idea, profile)     │    │
│  │   → Prompts com seções dinâmicas do domínio                   │    │
│  └─────────────────────┬──────────────────────────────────────────┘    │
│                        │                                                │
│  ┌─────────────────────▼──────────────────────────────────────────┐    │
│  │ ProponentAgent.expand(idea, expansion_prompt)                  │    │
│  │   → Proposta estruturada com seções dinâmicas                 │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────┬──────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  DEBATE ENGINE — Rounds 1+: Debate Adaptativo                           │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │ LOOP while round_num <= MAX_ROUNDS:                          │      │
│  │                                                              │      │
│  │ ┌─ Turn de Crítica ─────────────────────────────────────┐   │      │
│  │ │ DynamicPromptBuilder.build_critique_prompt()          │   │      │
│  │ │ CriticAgent.review() → Issues com categorias dinâmicas│   │      │
│  │ │ DebateStateTracker.extract_and_register(issues)      │   │      │
│  │ └───────────────────────────────────────────────────────┘   │      │
│  │                                                              │      │
│  │ ┌─ Orquestração ────────────────────────────────────────┐   │      │
│  │ │ AdaptiveOrchestrator.evaluate()                        │   │      │
│  │ │   → OrchestratorDecision(CONTINUE | STOP | SPAWN)    │   │      │
│  │ │   → Se SPAWN: category é do validation_schema dinâmico│   │      │
│  │ └───────────────────┬──────────────────────────────────┘   │      │
│  │                    │                                        │      │
│  │                    ├─ Se SPAWN ──────┐                      │      │
│  │                    │                  │                      │      │
│  │ ┌──────────────────▼─────────────────▼──────────────────┐   │      │
│  │ │ SpecialistFactory.get_or_create(category)             │   │      │
│  │ │ DynamicSpecialistAgent.audit()                         │   │      │
│  │ │ Issues registradas no board                           │   │      │
│  │ └────────────────────────────────────────────────────────┘   │      │
│  │                                                              │      │
│  │ ┌─ Turn de Defesa ──────────────────────────────────────┐   │      │
│  │ │ (se não STOP)                                         │   │      │
│  │ │ ProponentAgent.defend()                               │   │      │
│  │ │ Proposta atualizada                                   │   │      │
│  │ └───────────────────────────────────────────────────────┘   │      │
│  │                                                              │      │
│  │ ┌─ Decisão Final ───────────────────────────────────────┐   │      │
│  │ │ Se action = STOP: break                               │   │      │
│  │ │ Senão: round_num++                                    │   │      │
│  │ └───────────────────────────────────────────────────────┘   │      │
│  │                                                              │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                         │
└─────────────────┬──────────────────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  SÍNTESE E RELATÓRIO (Inalterado)                                       │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ SynthesizerAgent.generate_synthesis(board)                     │    │
│  │   → Markdown com Issues, Decisões, Pressupostos               │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │ ReportGenerator.generate(board, file_path)                     │    │
│  │   → Persiste relatório com timestamp                           │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────┬──────────────────────────────────────────────────────┘
                  │
                  ▼
            ┌──────────────┐
            │ Relatório MD │
            │ (Saída)      │
            └──────────────┘
```

### 1.2 Fluxo de Dados no Round 0A e 0B

```
┌─────────────────────────────────────────────────────────────────────────┐
│           CONTROLLER: ROUND 0A (META-ORQUESTRAÇÃO)                      │
└─────────────────────────────────────────────────────────────────────────┘

Entrada: Ideia Bruta (string)
         │
         ▼
    ┌────────────────────┐
    │ DomainDetector     │
    │ (100% programático)│
    └────────┬───────────┘
             │
             ▼
    DomainDetectionResult
    {
      domain: "business" | "software" | ... | "generic"
      confidence: float (0–1)
      matched_keywords: List[str]
    }
             │
             ▼
    ┌────────────────────────┐
    │ DomainContextBuilder   │
    │ (1 chamada LLM)        │
    └────────┬───────────────┘
             │
             ├─→ BRANCH A: LLM Success
             │   ├─ Response: JSON
             │   ├─ Parse: json.loads()
             │   └─ Validate: fields obrigatórios
             │
             ├─→ BRANCH B: JSON Parse Fails
             │   ├─ Tenta extrair JSON do texto
             │   └─ Se falhar: aplica BRANCH C
             │
             └─→ BRANCH C: Fallback Determinístico
                 └─ Carrega DOMAIN_FALLBACKS[domain]
             │
             ▼
    DomainProfile
    {
      domain: str
      confidence: float
      source: "llm" | "fallback"
      expansion_sections: List[ExpansionSection]
      validation_dimensions: List[ValidationDimension]
      report_sections: List[ReportSection]
      specialist_hints: List[str]
      critical_questions: List[str]
      success_criteria: Dict[str, str]
    }
             │
             ▼
    ┌──────────────────────────┐
    │ ValidationBoard          │
    │ .set_domain_profile(...) │
    └────────┬─────────────────┘
             │
             ▼
    Board internaliza:
    - _profile: DomainProfile
    - _validation_schema: Dict com categorias dinâmicas
    - Métodos: is_valid_category(), get_dominant_open_category()

┌─────────────────────────────────────────────────────────────────────────┐
│                      ROUND 0B: EXPANSÃO                                 │
└─────────────────────────────────────────────────────────────────────────┘

Entrada: Ideia Bruta (string) + DomainProfile (injetado no Board)
         │
         ▼
    ┌────────────────────────────┐
    │ DynamicPromptBuilder       │
    │ .build_expansion_prompt()  │
    └────────┬───────────────────┘
             │
             ├─ Contracts (invariantes):
             │  ├─ ANTI_PROLIXITY_DEBATE
             │  ├─ STYLE_CONTRACT_DEBATE
             │  └─ ISSUE_TABLE_HEADER
             │
             └─ Contexto (dinâmico):
                ├─ Domínio: profile.domain
                ├─ Seções: profile.expansion_sections
                └─ Instrução por seção: section.instruction
             │
             ▼
    Prompt montado:
    "Você é o Agente Proponente...
     DOMÍNIO: BUSINESS
     ESTRUTURA (6 Seções):
     1. Problema: ...instrução...
     2. Mercado: ...instrução...
     ..."
             │
             ▼
    ┌──────────────────────────┐
    │ ProponentAgent           │
    │ .expand(idea, prompt)    │
    └────────┬─────────────────┘
             │
             ▼
    Proposta Expandida
    (com seções dinâmicas)
```

### 1.3 Fluxo de Spawn Dinâmico (Rounds 1+)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SPAWN DINÂMICO DE ESPECIALISTAS                      │
└─────────────────────────────────────────────────────────────────────────┘

Round N: Issues coletadas no Board
         │
         ▼
    ┌─────────────────────────────────────────┐
    │ AdaptiveOrchestrator.evaluate()          │
    │ board.get_dominant_open_category()       │
    └──────────────┬──────────────────────────┘
                   │
                   ├─ Conta issues por categoria
                   │  (usando validation_schema dinâmico)
                   │
                   └─ Se categoria_dominante >= SPAWN_THRESHOLD:
                        │
                         ├─ Check: category not in _spawned_categories? (Deduplicação)
                         └─ Check: current_agent_count < MAX_AGENTS?
                             │
                             ├─ SIM: action = "SPAWN", category = "MARKET_FIT"
                             └─ NÃO: action = "CONTINUE"
                   │
                   ▼
    OrchestratorDecision
    {
      action: "SPAWN",
      reason: "Lacuna em MARKET_FIT",
      category: "MARKET_FIT"
    }
                   │
                   ▼
    ┌──────────────────────────────────────────┐
    │ SpecialistFactory.get_or_create()        │
    │   (if action == "SPAWN")                 │
    └──────────────┬───────────────────────────┘
                   │
                   ├─ Check: MARKET_FIT já foi spawnado?
                   │
                   ├─ NÃO: lookup DomainProfile.get_dimension_by_id("MARKET_FIT")
                   │       └─ Extract: display_name, spawn_hint, description
                   │
                   ▼
    DynamicSpecialistAgent
    {
      category: "MARKET_FIT"
      display_name: "Encaixe de Mercado"
      spawn_hint: "Especialista em Análise de Mercado"
      prompt_builder: DynamicPromptBuilder (referência)
    }
                   │
                   ▼
    ┌──────────────────────────────────────────┐
    │ DebateEngine                             │
    │   .specialist.audit(provider, proposal)  │
    └──────────────┬───────────────────────────┘
                   │
                   ├─ build_specialist_prompt():
                   │  "Você é um Especialista em Análise de Mercado...
                   │   DOMÍNIO: BUSINESS
                   │   FOCO: Encaixe de Mercado
                   │   ..."
                   │
                   ▼
    ┌──────────────────────────────────────────┐
    │ ModelProvider.generate()                 │
    │   (max_tokens=1000)                      │
    └──────────────┬───────────────────────────┘
                   │
                   ▼
    Audit Response (Markdown Table)
    ┌─────────────────────────────────────┐
    │ | Sev | Cat      | Descrição | Sug │
    │ |-----|----------|-----------|-----|
    │ | HIGH| MARKET_FIT| Demand unclear...│
    └─────────────────────────────────────┘
                   │
                   ▼
    ┌──────────────────────────────────────────┐
    │ DebateStateTracker                       │
    │ .extract_and_register_issues(response)   │
    └──────────────┬───────────────────────────┘
                   │
                   ├─ Parse table
                   ├─ CategoryNormalizer.normalize(cat)
                   ├─ Create IssueRecords
                   └─ board.add_issue()
                   │
                   ▼
    Board atualizado com issues do especialista
    (prontos para próximo turno de defesa)
```

---

## 2. Matriz de Decisões da Onda 4.0

### 2.1 Decisões Arquiteturais Centrais

| ID | Decisão | Racional | Alternativas Rejeitadas |
|---|---|---|---|
| **AD-1** | Meta-Orquestração no **Controller (Round 0A)** | Manter DebateEngine limpo, orquestrando descoberta de domínio na camada mais alta | Round 0A dentro do DebateEngine (sobrecarga) |
| **AD-2** | DomainDetector **100% programático** (sem LLM) | Determinismo, velocidade, testabilidade | Usar LLM para detecção (não determinístico) |
| **AD-3** | DomainContextBuilder **1 única chamada LLM** | Balancear flexibilidade com eficiência de tokens | Múltiplas chamadas LLM para cada aspecto (custoso) |
| **AD-4** | Fallback **determinístico pré-configurado** | Robustez garantida; sem dependência de LLM | Recursão (chamar LLM novamente) ou erro fatal |
| **AD-5** | DomainProfile **injetado no ValidationBoard** | Blackboard pattern; centralizar config; manter board como source of truth | Passar profile como parâmetro por cada agente (acoplamento) |
| **AD-6** | Categorias **dinâmicas no board** | Agnóstico a domínio; sem hardcoding | Criar novo Board para cada domínio (complexidade) |
| **AD-7** | SpecialistFactory **on-the-fly via DomainProfile** | Eliminar perfis estáticos; adaptar dinamicamente | Estender `specialist_profiles.py` com novos perfis (não escala) |
| **AD-8** | CategoryNormalizer **mapeia keywords** | Flexibilidade; aceita variações de nome | Apenas aceitar IDs exatos (rigidez) |
| **AD-9** | DynamicPromptBuilder **compõe prompts** | Separar contratos invariantes de contexto dinâmico | Templates com placeholders (menos modular) |
| **AD-10** | AdaptiveOrchestrator **inalterado na lógica** | Preservar rigor programático; muda apenas fonte de categorias | Reescrever lógica de spawn (risco de regressão) |

### 2.2 Trade-offs Arquiteturais

| Trade-off | Escolha | Benefício | Custo |
|---|---|---|---|
| **Simplicidade vs. Flexibilidade** | Flexibilidade (DomainProfile) | Suporta qualquer domínio sem recompilação | Mais módulos (6 novos), mais parâmetros |
| **Determinismo vs. Adaptação** | Determinismo (DomainDetector) + Adaptação (LLM 1x) | Fluxo confiável + configuração inteligente | 1 chamada LLM por sessão (custo fixo) |
| **Acoplamento vs. Centralização** | Centralização (Board como source of truth) | Menos duplicação de config | Todas as decisões consultam board |
| **Testes vs. Ciclo de Dev** | Testes robustos (TDD + integração) | Alta confiabilidade; retrocompatibilidade verificada | +36 testes; 2-3 semanas implementação |
| **Velocidade vs. Qualidade de Fallback** | Qualidade (fallbacks pré-configurados) | Nunca falha silenciosamente; sempre há config válida | Fallbacks precisam ser mantidos por domínio |

### 2.3 Matriz de Responsabilidades (RACI)

| Módulo | Responsável | Consulta | Informa | Aprova |
|---|---|---|---|---|
| DomainDetector | Arquiteto | Detector Config | DebateEngine | Tech Lead |
| DomainContextBuilder | Arquiteto | LLM Provider, Fallbacks | DebateEngine | Tech Lead |
| DomainProfile | Arquiteto | Schemas | ValidationBoard | Product |
| DynamicPromptBuilder | Arquiteto | Contratos Invariantes, Board, Profile | DebateEngine Agents | Tech Lead |
| SpecialistFactory | Arquiteto | Profile, Board | DebateEngine | Tech Lead |
| CategoryNormalizer | Arquiteto | Profile | DebateStateTracker | Tech Lead |
| ValidationBoard (evoluído) | Dev | Profile | Orchestrator | Tech Lead |
| AdaptiveOrchestrator | Dev | Board, `_spawned_categories` | DebateEngine | Tech Lead |
| Controller (Round 0A) | Dev | Detector, Builder | DebateEngine | Tech Lead |
| DebateEngine (integração) | Dev | Board | Controller | Tech Lead |

---

## 3. Análise de Riscos e Mitigações

### 3.1 Riscos de Implementação

| Risco | Severidade | Probabilidade | Mitigação |
|---|---|---|---|
| **R1**: JSON inválido do LLM | MED | ALTA | Extrator robusto + 5 fallbacks por domínio |
| **R2**: Regressão nos 119 testes da Onda 3 | ALTA | MED | Todos os novos parâmetros têm defaults |
| **R3**: Explosão de especialistas | MED | BAIXA | `MAX_AGENTS` limite + cache `_spawned_categories` |
| **R4**: Performance degradada (Round 0A) | BAIXA | MED | LLM chamada única (400 tokens) + cache possível na v4.1 |
| **R5**: Domínios novos descobertos em produção | MED | ALTA | Fallback "generic" + mecanismo para adicionar novos domínios sem recompilação |
| **R6**: Normalização de categorias errada | LOW | BAIXA | Testes de keyword matching + override manual via CategoryNormalizer |
| **R7**: Memory leak em SpecialistFactory | LOW | BAIXA | Usar `@dataclass` + cleanup explícito após debate |

### 3.2 Plano de Mitigação de Riscos

**R1 — JSON Inválido**
```python
# src/core/domain_context_builder.py
try:
    data = json.loads(response)
except JSONDecodeError:
    data = extract_json_from_markdown(response)
    if not data:
        data = apply_fallback(detected_domain)
# Sempre retorna um DomainProfile válido
```

**R2 — Regressão de Testes**
```python
# Todos os módulos novos verificam defaults
def __init__(self, board, profile: Optional[DomainProfile] = None):
    self.profile = profile or get_default_profile()
    # Se profile=None, usa profile "classic" (compatibilidade Onda 3)
```

**R3 — Explosão de Especialistas**
```python
class AdaptiveOrchestrator:
    def evaluate(self):
        if self._current_agent_count >= self._max_agents:
            return OrchestratorDecision(action="STOP", ...)
        if category in self._spawned_categories:
            return OrchestratorDecision(action="CONTINUE", ...)
```

**R4 — Performance**
- Round 0A = DomainDetector (< 100ms) + LLM (1x, 400 tokens ~ 2-5s)
- Impacto: +2-5s por sessão (aceitável; economia de tokens em rounds posteriores)

**R5 — Novos Domínios**
```python
# Mecanismo para usuário adicionar domínios sem recompilação
# src/config/domains.json
{
  "custom_domain": {
    "keywords": [...],
    "expansion_sections": [...],
    "validation_dimensions": [...]
  }
}
```

---

## 4. Comparação Onda 3 vs. Onda 4.0

### 4.1 Tabela Comparativa

| Aspecto | Onda 3 | Onda 4.0 | Melhoria |
|---|---|---|---|
| **Domínios suportados** | Software (hardcoded) | Qualquer domínio (genérico) | +∞ (extensível) |
| **Categorias de issues** | 6 fixas (SECURITY, etc.) | Dinâmicas por DomainProfile | Sem limite |
| **Especialistas** | 4 perfis estáticos | Factory on-the-fly | Escalável |
| **Prompts** | Templates estáticos | Composição dinâmica | Flexível |
| **Calls LLM por sessão** | ~N+2 (Proponent + N Critics) | ~N+3 (DomainContextBuilder + N+ Specialists) | +1 call (1% impacto) |
| **Tempo de setup** | < 1s | ~3-5s (Round 0A) | Trade-off: flexibilidade |
| **Linhas de código** | 1200+ | 1200 + 800 novos | +67% código (modularizado) |
| **Retrocompatibilidade** | N/A | 100% (defaults) | ✅ Todos testes passam |
| **Extensibilidade** | Baixa (recompilação) | Alta (configuração) | 10x mais flexível |

### 4.2 Ganhos de Arquitetura

| Ganho | Impacto |
|---|---|
| **Meta-Orquestração separada** | Concern separation; mais testável |
| **Fallbacks determinísticos** | Nunca falha; sempre há config válida |
| **Board como Blackboard** | Single source of truth; reduz duplicação |
| **SpecialistFactory** | Elimina hardcoding; escala com demanda |
| **DynamicPromptBuilder** | Prompts agnósticos; compõe na hora |
| **CategoryNormalizer** | Aceita variações; menos erros de parsing |

---

## 5. Exemplos de Uso Passo a Passo

### 5.1 Exemplo: Debate de Negócio

```
Input: "Marketplace de roupas circulares com subscription model"

┌─ Round 0A: Meta-Orquestração
│  ├─ DomainDetector: "marketplace", "subscription", "negócio"
│  │  → domain="business", confidence=0.89
│  │
│  └─ DomainContextBuilder:
│     Prompt: "Analisar ideia e retornar JSON com:
│              - expansion_sections para negócio
│              - validation_dimensions: MARKET_FIT, UNIT_ECONOMICS, etc.
│              - specialist_hints"
│     LLM Response: {
│       "expansion_sections": [
│         {"id": "PROBLEM", "title": "Definição do Problema"},
│         {"id": "TARGET_MARKET", ...},
│         {"id": "REVENUE_MODEL", ...},
│         ...
│       ],
│       "validation_dimensions": [
│         {"id": "MARKET_FIT", "display_name": "Encaixe de Mercado", ...},
│         {"id": "UNIT_ECONOMICS", ...},
│         ...
│       ],
│       "specialist_hints": ["Economista", "Especialista em Logística", ...]
│     }
│     
│     ValidationBoard.set_domain_profile(profile)
│     → _validation_schema = {
│         "MARKET_FIT": {...},
│         "UNIT_ECONOMICS": {...},
│         ...
│       }

├─ Round 0B: Expansão
│  └─ DynamicPromptBuilder.build_expansion_prompt():
│     "Você é o Agente Proponente...
│      DOMÍNIO: BUSINESS
│      ESTRUTURA OBRIGATÓRIA:
│      1. Definição do Problema: [instrução específica]
│      2. Mercado Alvo: [instrução específica]
│      3. Modelo de Receita: [instrução específica]
│      ..."
│     
│     ProponentAgent.expand():
│     # Proposta com seções de negócio (não software)

├─ Round 1: Crítica
│  └─ Crítico recebe prompts com categorias dinâmicas:
│     "CATEGORIAS PERMITIDAS:
│      - MARKET_FIT: Demanda de mercado
│      - UNIT_ECONOMICS: Viabilidade econômica
│      - GO_TO_MARKET: Estratégia de entrada
│      ..."
│     
│     Issues extraídas: categoria="MARKET_FIT" (válida no schema)

├─ Round 2: Orquestração detecta 3 issues em MARKET_FIT
│  └─ Decision: SPAWN (category="MARKET_FIT")
│     
│     SpecialistFactory.get_or_create("MARKET_FIT"):
│     → DynamicSpecialistAgent(
│         category="MARKET_FIT",
│         spawn_hint="Especialista em Análise de Mercado"
│       )

├─ Round 2b: Especialista de Mercado audita
│  └─ DynamicPromptBuilder.build_specialist_prompt("MARKET_FIT"):
│     "Você é um Especialista em Análise de Mercado...
│      FOCO: Encaixe de Mercado
│      [tabela com issues vigentes]"
│     
│     Auditoria: encontra mais 2 issues relacionadas a demand validation

└─ Rounds 3+: Debate continua até convergência ou MAX_ROUNDS
   
   Final: Relatório com Issues/Decisions/Assumptions
   (sem mudança em relação à Onda 3)
```

### 5.2 Exemplo: Fallback (LLM Falha)

```
Input: "Ideia de evento virtual de educação"

├─ DomainDetector: domain="education", confidence=0.71
│
├─ DomainContextBuilder.build():
│  ├─ LLM prompt...
│  ├─ LLM responde: "Aqui está a análise: [CORRUPTED JSON] ..."
│  ├─ json.loads() fails
│  ├─ extract_json_from_markdown() fails
│  └─ apply_fallback("education"):
│     Carrega DOMAIN_FALLBACKS["education"] pré-configurado
│     → DomainProfile com:
│        - expansion_sections: PROBLEM, PEDAGOGY, CONTENT, DELIVERY, etc.
│        - validation_dimensions: PEDAGOGY, ACCESSIBILITY, ENGAGEMENT, etc.
│
└─ Debate continua com profile fallback
   (Qualidade um pouco menor, mas funcional)
```

---

## 6. Próximos Passos (Onda 4.1+)

### 6.1 Melhorias Futuras

| Melhoria | Fase | Descrição |
|---|---|---|
| **Cache LLM** | 4.1 | Cache de respostas de `DomainContextBuilder` por ideia hash |
| **Dashboard Gradio** | 4.1 | Visualização em tempo real do debate |
| **User-defined Domains** | 4.2 | Config JSON para adicionar novos domínios em runtime |
| **Weighted Categories** | 4.2 | Spawn por prioridade (não apenas count de issues) |
| **Specialist Pooling** | 4.2 | Reusar especialista se categoria re-spawn dentro de N rounds |
| **Localization** | 4.3 | Suporte a múltiplos idiomas em prompts |

### 6.2 Indicadores de Sucesso (Onda 4.0)

- ✅ 155+ testes passando (119 + 36 novos)
- ✅ Smoke test: 3 domínios (software, business, philosophy)
- ✅ Tempo Round 0A + 0B < 10s
- ✅ Tokens por sessão reduzem (melhor que Onda 3)
- ✅ Zero regressão nos 119 testes da Onda 3
- ✅ Documentação 100% (docstrings + exemplos)

---

Fim do Documento de Arquitetura.
