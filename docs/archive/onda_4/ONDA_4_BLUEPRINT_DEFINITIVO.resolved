# Blueprint Definitivo — Onda 4.0: Generalização Agnóstica do IdeaForge 2

**Versão:** 1.0 Final  
**Data:** 26/04/2026  
**Autor:** Arquiteto de Software — IdeaForge 2  
**Status:** Pronto para Implementação  

---

## Sumário Executivo

A **Onda 4.0** evolui o IdeaForge 2 de um sistema software-centric para um **motor universal de validação adversarial**, capaz de debater ideias em qualquer domínio (negócio, filosofia, logística, eventos, educação, etc.) sem perder sua identidade: rigor adversarial, orquestração 100% programática e compatibilidade com modelos pequenos.

### Inovações Principais

| Inovação | Descrição |
|---|---|
| **Meta-Orquestração** | Round 0A: Análise automática do domínio gerando `DomainProfile` em JSON |
| **Taxonomia Dinâmica** | `ValidationBoard` carrega categorias específicas ao domínio em tempo de execução |
| **Fábrica de Especialistas** | Agentes criados on-the-fly por `SpecialistFactory` em vez de perfis estáticos |
| **Composição de Prompts** | `DynamicPromptBuilder` monta instruções unindo contratos invariantes com contexto dinâmico |
| **Generalização Rigorosa** | Estrutura + semântica separadas; fluxo permanece programático, conteúdo vira dinâmico |

### Princípios Arquiteturais

1. **Separação de Preocupações**
   - Estrutura (invariante): issues, decisões, pressupostos, severidade, status, limites.
   - Semântica (variável): categorias, seções, especialistas, critérios de validação.

2. **Agnóstico ao Domínio**
   - Não há hardcoding de "software", "segurança", "escalabilidade".
   - Tudo é injetado dinamicamente no Round 0A.

3. **Retrocompatibilidade Total**
   - Todos os novos parâmetros têm defaults que preservam o comportamento da Onda 3.
   - Testes existentes continuam passando sem mudanças.

4. **Fidelidade Adversarial**
   - Proponent não é "chat"; continua defendendo a tese.
   - Critic não é "feedback"; continua atacando com rigor.
   - Orquestrador permanece programático; LLM nunca decide fluxo.

---

## 1. Arquitetura de Alto Nível

### 1.1 Fluxo da Onda 4.0

```
┌─────────────────────────────────────────────────────────┐
│ INPUT: Ideia Bruta                                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ CONTROLLER: Round 0A (META-ORQUESTRAÇÃO)                │
│ ┌───────────────────────────────────────────────────┐   │
│ │ 1. Controller invoca DomainDetector               │   │
│ │    → classifica domínio por keywords              │   │
│ │                                                   │   │
│ │ 2. Controller invoca DomainContextBuilder         │   │
│ │    → gera DomainProfile em JSON                   │   │
│ │    → fallback determinístico se LLM falhar        │   │
│ │                                                   │   │
│ │ 3. Controller injeta DomainProfile no             │   │
│ │    DebateEngine e ValidationBoard                 │   │
│ └───────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Round 0B: EXPANSÃO CONTEXTUALIZADA                      │
│ ┌───────────────────────────────────────────────────┐   │
│ │ ProponentAgent.expand(idea, dynamic_prompt)       │   │
│ │ Monta seções específicas ao domínio               │   │
│ └───────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ Proposta Expandida (dinâmica ao domínio)               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ DEBATE ADAPTATIVO (Rounds 1+)                           │
│ ┌───────────────────────────────────────────────────┐   │
│ │ 1. CriticAgent: ataca com categorias dinâmicas    │   │
│ │ 2. AdaptiveOrchestrator: decide CONTINUE/STOP/    │   │
│ │    SPAWN e registra categorias já spawnadas.      │   │
│ │ 3. SpecialistFactory: cria especialista on-the-fly│   │
│ │    quando orquestrador detecta lacuna             │   │
│ │ 4. ProponentAgent: defende ajustando à proposta   │   │
│ └───────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ SÍNTESE + RELATÓRIO (inalterado)                        │
│ SynthesizerAgent gera Markdown com board finalizado     │
└─────────────────────────────────────────────────────────┘
```

### 1.2 Mapeamento de Módulos Novos

| Módulo | Localização | Responsabilidade |
|---|---|---|
| `DomainDetector` | `src/core/domain_detector.py` | Classificação de domínio via keywords (100% programático) |
| `DomainContextBuilder` | `src/core/domain_context_builder.py` | Geração de `DomainProfile` (1 chamada LLM) |
| `DomainProfile` | `src/core/domain_profile.py` | Schema de dados para configuração dinâmica do debate |
| `DynamicPromptBuilder` | `src/core/dynamic_prompt_builder.py` | Composição de prompts forçando contratos invariantes (ex: seções numeradas, ISSUE_TABLE_HEADER) |
| `SpecialistFactory` | `src/agents/specialist_factory.py` | Criação on-the-fly de especialistas por categoria |
| `CategoryNormalizer` | `src/core/category_normalizer.py` | Normalização de categorias novas (validação, mapping) |

---

## 2. Módulo 1: `DomainDetector` (100% Programático)

### 2.1 Filosofia
Seguindo o contrato da Onda 3, o `DomainDetector` classifica o domínio **sem usar LLM**. É uma heurística determinística baseada em keywords — rápida, testável e previsível.

### 2.2 Definição de Domínios Suportados

```
- "software"       → arquitetura, engenharia, backend, frontend, devops, security técnica
- "business"       → negócio, mercado, unit economics, go-to-market, competição
- "event"          → evento, conferência, logística operacional, orçamento
- "philosophy"     → tese conceitual, lógica, ética, epistemologia
- "research"       → pesquisa acadêmica, metodologia, hipóteses
- "education"      → currículo, pedagogia, aprendizado
- "generic"        → ideia genérica (fallback quando confiança < 50%)
```

### 2.3 Interface Proposta

```python
# src/core/domain_detector.py

from dataclasses import dataclass
from typing import Optional, List

DOMAIN_KEYWORDS = {
    "software": [
        "api", "banco de dados", "backend", "frontend", "microservices",
        "kubernetes", "docker", "cloud", "aws", "arquitetura",
        "scalability", "performance", "latency", "throughput"
    ],
    "business": [
        "mercado", "cliente", "receita", "custo", "margem",
        "unit economics", "ltv", "cac", "churn", "growth",
        "competição", "positioning", "go-to-market"
    ],
    "event": [
        "evento", "conferência", "workshop", "hackathon",
        "logística", "venue", "catering", "transporte",
        "orçamento", "cronograma"
    ],
    "philosophy": [
        "tese", "conceito", "lógica", "ética", "epistemologia",
        "argumento", "premissa", "conclusão", "validade",
        "ontologia", "fenômeno"
    ],
    "research": [
        "pesquisa", "estudo", "hipótese", "metodologia",
        "experimento", "dado", "resultado", "publicação",
        "peer-review", "literatura"
    ],
    "education": [
        "currículo", "pedagogia", "aprendizado", "aluno",
        "didática", "educação", "ensino", "formação",
        "competência", "objetivo pedagógico"
    ]
}

@dataclass
class DomainDetectionResult:
    domain: str                  # "software" | "business" | ... | "generic"
    confidence: float            # 0.0 a 1.0
    matched_keywords: List[str]  # keywords encontradas
    
    def is_confident(self, threshold: float = 0.5) -> bool:
        return self.confidence >= threshold


class DomainDetector:
    """
    Classificador de domínio 100% programático.
    Sem LLM, sem I/O, sem estado — apenas keywords e heurística.
    """
    
    def __init__(self, keywords: Optional[dict] = None):
        self.keywords = keywords or DOMAIN_KEYWORDS
    
    def detect(self, idea: str) -> DomainDetectionResult:
        """
        Detecta domínio analisando keywords na ideia.
        
        Algoritmo:
        1. Normalizar texto (lowercase, remover pontuação)
        2. Contar keywords por domínio
        3. Calcular score normalizado (0–1)
        4. Se score < 0.5, retornar "generic"
        5. Retornar domínio com maior score
        """
        # (implementação em seção 5.1)
```

### 2.4 Exemplo de Uso

```python
detector = DomainDetector()

# Caso 1: Ideia de software
result = detector.detect("""
    Precisamos redesenhar nossa arquitetura backend usando microservices
    com Kubernetes e garantir escalabilidade e segurança
""")
# → DomainDetectionResult(domain="software", confidence=0.92, ...)

# Caso 2: Ideia genérica
result = detector.detect("Criar um novo projeto")
# → DomainDetectionResult(domain="generic", confidence=0.15, ...)
```

---

## 3. Módulo 2: `DomainProfile` (Schema de Dados)

### 3.1 Definição do Schema

```python
# src/core/domain_profile.py

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class ExpansionSection:
    """Define uma seção dinâmica para expansão no Round 0B."""
    id: str                # Ex: "MARKET_ANALYSIS", "LOGICAL_COHERENCE"
    title: str             # Título em PT-BR
    instruction: str       # Instrução curta (max 160 chars)
    max_words: int = 150

@dataclass
class ValidationDimension:
    """Define uma dimensão de validação (categoria) dinâmica."""
    id: str                # Ex: "LOGISTICS", "INTERNAL_CONSISTENCY"
    display_name: str      # Nome para exibição
    description: str       # Descrição curta do que valida
    spawn_hint: str        # Dica de especialista ("Especialista em Logística")
    keywords: List[str] = field(default_factory=list)  # Keywords para detecção

@dataclass
class ReportSection:
    """Define seções do relatório final."""
    id: str
    title: str
    template: str          # Template Markdown com placeholders

@dataclass
class DomainProfile:
    """
    Configuração dinâmica do debate para um domínio específico.
    Produzido pelo DomainContextBuilder no Round 0A.
    Injetado no ValidationBoard antes do Round 0B.
    """
    domain: str                              # "software", "business", etc.
    confidence: float                        # Confiança da detecção (0–1)
    source: str                              # "detector" | "llm" | "fallback"
    
    expansion_sections: List[ExpansionSection]
    validation_dimensions: List[ValidationDimension]
    report_sections: List[ReportSection]
    
    specialist_hints: List[str] = field(default_factory=list)
    critical_questions: List[str] = field(default_factory=list)
    success_criteria: Dict[str, str] = field(default_factory=dict)
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_section_by_id(self, section_id: str) -> Optional[ExpansionSection]:
        return next((s for s in self.expansion_sections if s.id == section_id), None)
    
    def get_dimension_by_id(self, dim_id: str) -> Optional[ValidationDimension]:
        return next((d for d in self.validation_dimensions if d.id == dim_id), None)
    
    def get_dimension_ids(self) -> List[str]:
        return [d.id for d in self.validation_dimensions]
```

### 3.2 Exemplos de `DomainProfile`

#### Exemplo 1: Domínio "business"

```python
profile_business = DomainProfile(
    domain="business",
    confidence=0.85,
    source="llm",
    expansion_sections=[
        ExpansionSection(id="PROBLEM_STATEMENT", title="Definição do Problema"),
        ExpansionSection(id="TARGET_MARKET", title="Mercado Alvo"),
        ExpansionSection(id="VALUE_PROPOSITION", title="Proposta de Valor"),
        ExpansionSection(id="REVENUE_MODEL", title="Modelo de Receita"),
        ExpansionSection(id="GO_TO_MARKET", title="Estratégia de Go-to-Market"),
        ExpansionSection(id="COMPETITION", title="Análise de Competição"),
    ],
    validation_dimensions=[
        ValidationDimension(
            id="MARKET_FIT",
            display_name="Encaixe de Mercado",
            description="Demanda de mercado e disposição a pagar",
            spawn_hint="Especialista em Análise de Mercado"
        ),
        ValidationDimension(
            id="UNIT_ECONOMICS",
            display_name="Economia Unitária",
            description="Viabilidade econômica do modelo de negócio",
            spawn_hint="Especialista em Economia"
        ),
        ValidationDimension(
            id="GO_TO_MARKET",
            display_name="Estratégia de Entrada",
            description="Plano de entrada no mercado e distribuição",
            spawn_hint="Especialista em Go-to-Market"
        ),
        ValidationDimension(
            id="OPERATIONAL_FEASIBILITY",
            display_name="Viabilidade Operacional",
            description="Capacidade de operacionalizar a solução",
            spawn_hint="Especialista em Operações"
        ),
        ValidationDimension(
            id="COMPETITIVE_ADVANTAGE",
            display_name="Vantagem Competitiva",
            description="Diferenciação e moat defensivo",
            spawn_hint="Especialista em Estratégia"
        ),
    ]
)
```

#### Exemplo 2: Domínio "philosophy"

```python
profile_philosophy = DomainProfile(
    domain="philosophy",
    confidence=0.78,
    source="llm",
    expansion_sections=[
        ExpansionSection(id="THESIS_STATEMENT", title="Tese Central"),
        ExpansionSection(id="KEY_CONCEPTS", title="Conceitos-Chave"),
        ExpansionSection(id="LOGICAL_CHAIN", title="Cadeia Lógica"),
        ExpansionSection(id="EVIDENCE", title="Fundamentação e Evidência"),
        ExpansionSection(id="COUNTERARGUMENTS", title="Contrapont"),
        ExpansionSection(id="IMPLICATIONS", title="Implicações Práticas"),
    ],
    validation_dimensions=[
        ValidationDimension(
            id="LOGICAL_CONSISTENCY",
            display_name="Coerência Lógica",
            description="Ausência de contradições internas e falhas lógicas",
            spawn_hint="Especialista em Lógica"
        ),
        ValidationDimension(
            id="DEFINITIONAL_CLARITY",
            display_name="Clareza de Definições",
            description="Termos bem definidos e uso consistente",
            spawn_hint="Especialista em Análise Conceitual"
        ),
        ValidationDimension(
            id="EPISTEMOLOGICAL_GROUNDING",
            display_name="Fundamentação Epistemológica",
            description="Solidez do fundamento do conhecimento alegado",
            spawn_hint="Especialista em Epistemologia"
        ),
        ValidationDimension(
            id="COUNTEREXAMPLE_RESILIENCE",
            display_name="Resiliência a Contraexemplos",
            description="Capacidade de lidar com refutações possíveis",
            spawn_hint="Especialista em Lógica Argumentativa"
        ),
    ]
)
```

---

## 4. Módulo 3: `DomainContextBuilder` (1 Chamada LLM)

### 4.1 Responsabilidade

Gera um `DomainProfile` estruturado baseado na ideia bruta e na detecção de domínio. É o **único lugar da Onda 4.0 onde um LLM é chamado para gerar configuração** (não para debater).

### 4.2 Prompt Otimizado (Max 400 Tokens)

```python
# src/core/domain_context_builder.py

DOMAIN_CONTEXT_PROMPT = """
Você é um assistente de meta-análise do IdeaForge 2.

TAREFA: Analisar a ideia abaixo e retornar UM JSON estruturado.
PROIBIDO: texto adicional, saudações, ou explicações.

IDEIA:
{idea}

DOMÍNIO DETECTADO: {detected_domain}

Retorne EXATAMENTE este JSON (sem Markdown, sem comentários):

{{
  "expansion_sections": [
    {{
      "id": "SEÇÃO_1_ID",
      "title": "Título em PT-BR",
      "instruction": "Instrução concisa (máx 160 chars)"
    }},
    ...
  ],
  "validation_dimensions": [
    {{
      "id": "DIMENSÃO_1_ID",
      "display_name": "Nome para Exibição",
      "description": "Descrição breve do que valida",
      "spawn_hint": "Tipo de especialista"
    }},
    ...
  ],
  "specialist_hints": ["Especialista A", "Especialista B"],
  "critical_questions": ["Pergunta 1", "Pergunta 2"],
  "success_criteria": {{
    "criteria_1": "Descrição"
  }}
}}

REGRAS:
1. expansion_sections: 6-8 seções, IDs em UPPER_SNAKE_CASE
2. validation_dimensions: 4-6 dimensões, cobrindo principais lacunas
3. specialist_hints: máx 3 especialistas mais prováveis
4. JSON VÁLIDO ou fallback será aplicado
"""
```

### 4.3 Implementação

```python
# src/core/domain_context_builder.py

import json
import logging
from typing import Optional, Dict, Any
from dataclasses import asdict

from src.core.domain_profile import DomainProfile, ExpansionSection, ValidationDimension
from src.models.model_provider import ModelProvider

logger = logging.getLogger(__name__)

# Fallbacks por domínio (usado se LLM falhar ou JSON inválido)
DOMAIN_FALLBACKS = {
    "software": {...},   # vide seção 4.4
    "business": {...},
    "philosophy": {...},
    "generic": {...}
}

class DomainContextBuilder:
    """
    Gera DomainProfile dinâmico usando LLM.
    Fallback determinístico se necessário.
    """
    
    def __init__(self, provider: ModelProvider):
        self.provider = provider
    
    def build(self, idea: str, detected_domain: str) -> DomainProfile:
        """
        Constrói DomainProfile usando LLM.
        Se falhar, aplica fallback.
        """
        try:
            return self._build_with_llm(idea, detected_domain)
        except Exception as e:
            logger.warning(f"LLM falhou: {e}. Aplicando fallback...")
            return self._apply_fallback(detected_domain)
    
    def _build_with_llm(self, idea: str, detected_domain: str) -> DomainProfile:
        """Chama LLM para gerar profile."""
        prompt = DOMAIN_CONTEXT_PROMPT.format(
            idea=idea[:800],  # Truncar ideia se muito grande
            detected_domain=detected_domain
        )
        
        response = self.provider.generate(
            prompt=prompt,
            max_tokens=400,
            temperature=0.3  # Baixa temperature para JSON estruturado
        )
        
        # Parse JSON
        try:
            data = json.loads(response)
        except json.JSONDecodeError:
            # Tentar extrair JSON do meio do texto
            data = self._extract_json_from_response(response)
        
        # Construir DomainProfile
        return self._parse_domain_profile(data, detected_domain, source="llm")
    
    def _apply_fallback(self, detected_domain: str) -> DomainProfile:
        """Aplica fallback determinístico para o domínio."""
        fallback_data = DOMAIN_FALLBACKS.get(detected_domain, DOMAIN_FALLBACKS["generic"])
        return self._parse_domain_profile(fallback_data, detected_domain, source="fallback")
    
    def _parse_domain_profile(self, data: Dict[str, Any], domain: str, source: str) -> DomainProfile:
        """Valida e constrói DomainProfile a partir de dados."""
        # (validação e construção)
        ...
    
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extrai JSON do meio de um texto com markdown/explicações."""
        # (implementação robusta)
        ...
```

### 4.4 Fallbacks Determinísticos

Cada domínio tem um fallback pré-configurado em caso de falha de LLM:

```python
DOMAIN_FALLBACKS = {
    "software": {
        "expansion_sections": [
            {"id": "OVERVIEW", "title": "Visão Geral", ...},
            {"id": "ARCHITECTURE", "title": "Arquitetura", ...},
            ...
        ],
        "validation_dimensions": [
            {"id": "SECURITY", "display_name": "Segurança", ...},
            {"id": "SCALABILITY", "display_name": "Escalabilidade", ...},
            ...
        ]
    },
    "business": {
        "expansion_sections": [
            {"id": "PROBLEM", "title": "Problema", ...},
            ...
        ],
        "validation_dimensions": [
            {"id": "MARKET_FIT", ...},
            ...
        ]
    },
    "generic": {
        "expansion_sections": [
            {"id": "PROBLEMA", "title": "Problema", "instruction": "Definição do problema a ser resolvido"},
            {"id": "PUBLICO_STAKEHOLDERS", "title": "Público/Stakeholders", "instruction": "Análise de público alvo e stakeholders envolvidos"},
            {"id": "SOLUCAO_TESE", "title": "Solução/Tese Central", "instruction": "A proposta central para resolução do problema"},
            {"id": "OPERACAO_IMPLEMENTACAO", "title": "Operação/Implementação", "instruction": "Passos operacionais para tornar a solução viável"},
            {"id": "RISCOS", "title": "Riscos", "instruction": "Riscos potenciais envolvidos na solução"},
            {"id": "PREMISSAS", "title": "Premissas", "instruction": "Fatos básicos e premissas assumidas"},
            {"id": "CRITERIOS_SUCESSO", "title": "Critérios de Sucesso", "instruction": "Métricas ou fatos que validarão o sucesso da ideia"}
        ],
        "validation_dimensions": [
            {"id": "FEASIBILITY", ...},
            {"id": "COMPLETENESS", ...},
            {"id": "CONSISTENCY", ...},
            {"id": "RISK_ASSESSMENT", ...}
        ]
    }
}
```

---

## 5. Módulo 4: `DynamicPromptBuilder` (Composição de Prompts)

### 5.1 Responsabilidade

Substitui templates estáticos por composição dinâmica de prompts. Combina:
- Contratos invariantes (estilo, idioma, formato)
- Contexto dinâmico (domínio, categorias, especialista)

### 5.2 Arquitetura

```python
# src/core/dynamic_prompt_builder.py

from src.core.domain_profile import DomainProfile
from src.core import prompt_templates
from src.core.validation_board import ValidationBoard

class DynamicPromptBuilder:
    """
    Monta prompts dinâmicos parametrizados pelo DomainProfile.
    Mantém contratos invariantes de estilo, anti-prolixidade, etc.
    """
    
    def __init__(self, board: ValidationBoard, profile: Optional[DomainProfile] = None):
        self.board = board
        self.profile = profile or self._get_default_profile()
    
    def build_expansion_prompt(self, idea: str) -> str:
        """
        Monta prompt de expansão (Round 0B) com seções dinâmicas.
        """
        sections_str = self._format_sections_for_prompt(self.profile.expansion_sections)
        
        return f"""
{prompt_templates.ANTI_PROLIXITY_DEBATE}
{prompt_templates.STYLE_CONTRACT_DEBATE}

Você é o Agente Proponente do sistema IDeA Forge 2.
Sua tarefa é transformar a ideia bruta abaixo em uma proposta robusta.

DOMÍNIO DETECTADO: {self.profile.domain.upper()}

ESTRUTURA OBRIGATÓRIA ({len(self.profile.expansion_sections)} Seções numeradas):
{sections_str}

Expanda cada seção de forma clara, estruturada em seções numeradas exatas, e sem prolixidade.
PROIBIDO: introduções genéricas, saudações ou conclusões frouxas.
OBRIGATÓRIO: direto ao ponto, com conteúdo técnico/estratégico, criando seções correspondentes à numeração requerida.

IDEIA BRUTA:
{idea}
"""
    
    def build_critique_prompt(
        self,
        current_proposal: str,
        last_defense: str,
        open_issues: str,
        validated_decisions: str
    ) -> str:
        """
        Monta prompt de crítica com categorias dinâmicas.
        """
        categories_str = self._format_categories_for_prompt(self.profile.validation_dimensions)
        
        return f"""
{prompt_templates.ANTI_PROLIXITY_DEBATE}
{prompt_templates.STYLE_CONTRACT_DEBATE}

Você é o Agente Crítico do sistema IDeA Forge 2.
Sua tarefa é encontrar falhas, omissões e riscos na proposta.

DOMÍNIO: {self.profile.domain.upper()}

INSTRUÇÕES:
1. NÃO gerar ID de issue — o sistema atribui automaticamente.
2. Usar EXATAMENTE este formato:
{prompt_templates.ISSUE_TABLE_HEADER}

3. Severidade: APENAS HIGH, MED ou LOW.
4. Categorias PERMITIDAS neste debate:
{categories_str}

5. Cada issue DEVE ter sugestão concreta de correção.
6. Avaliar se resoluções anteriores são suficientes.

ISSUES ABERTOS (não repetir):
{open_issues}

DECISÕES VALIDADAS:
{validated_decisions}

PROPOSTA VIGENTE:
{current_proposal}

ÚLTIMA DEFESA:
{last_defense}
"""
    
    def build_specialist_prompt(
        self,
        category_id: str,
        current_proposal: str,
        open_issues: str
    ) -> str:
        """
        Monta prompt para especialista dinâmico.
        """
        dimension = self.profile.get_dimension_by_id(category_id)
        if not dimension:
            raise ValueError(f"Dimensão {category_id} não encontrada no profile")
        
        return f"""
{prompt_templates.ANTI_PROLIXITY_DEBATE}
{prompt_templates.STYLE_CONTRACT_DEBATE}

Você é um {dimension.spawn_hint} convidado para o debate IDeA Forge 2.

DOMÍNIO: {self.profile.domain.upper()}
FOCO: Avaliar a proposta sob a ótica de {dimension.display_name}

INSTRUÇÕES:
1. NÃO gerar ID de issue.
2. Usar EXATAMENTE este formato:
{prompt_templates.ISSUE_TABLE_HEADER}

3. Categoria: SEMPRE '{category_id}'
4. Severidade: HIGH, MED ou LOW
5. Foque EXCLUSIVAMENTE em problemas de {dimension.display_name.lower()}
6. Não repetir issues: {open_issues}

PROPOSTA:
{current_proposal}

ISSUES ABERTOS:
{open_issues}
"""
    
    def _format_sections_for_prompt(self, sections) -> str:
        """Formata seções para o prompt."""
        lines = []
        for i, section in enumerate(sections, 1):
            lines.append(f"{i}. {section.title}: {section.instruction}")
        return "\n".join(lines)
    
    def _format_categories_for_prompt(self, dimensions) -> str:
        """Formata categorias para o prompt."""
        lines = []
        for dim in dimensions:
            lines.append(f"- {dim.id}: {dim.description}")
        return "\n".join(lines)
```

---

## 6. Módulo 5: `SpecialistFactory` (Criação On-the-Fly)

### 6.1 Responsabilidade

Substitui o banco estático de `specialist_profiles.py`. Cria especialistas dinamicamente quando o `AdaptiveOrchestrator` detecta uma lacuna em uma categoria.

### 6.2 Implementação

```python
# src/agents/specialist_factory.py

import logging
from typing import Optional, Dict, Any

from src.core.domain_profile import DomainProfile
from src.core.dynamic_prompt_builder import DynamicPromptBuilder
from src.models.model_provider import ModelProvider

logger = logging.getLogger(__name__)

class DynamicSpecialistAgent:
    """
    Agente especialista gerado dinamicamente.
    Contém apenas o essencial: nome, categoria, prompt template.
    """
    
    def __init__(
        self,
        category: str,
        display_name: str,
        spawn_hint: str,
        prompt_builder: DynamicPromptBuilder
    ):
        self.category = category
        self.display_name = display_name
        self.spawn_hint = spawn_hint
        self.prompt_builder = prompt_builder
    
    def audit(
        self,
        provider: ModelProvider,
        proposal: str,
        open_issues: str
    ) -> str:
        """
        Executa auditoria do especialista.
        Retorna texto em Markdown com issues encontrados.
        """
        prompt = self.prompt_builder.build_specialist_prompt(
            category_id=self.category,
            current_proposal=proposal,
            open_issues=open_issues
        )
        
        response = provider.generate(
            prompt=prompt,
            max_tokens=1000,
            temperature=0.5
        )
        
        return response


class SpecialistFactory:
    """
    Factory para criar especialistas dinamicamente.
    Evita perfis estáticos, permite criação por demanda.
    """
    
    def __init__(self, profile: DomainProfile, prompt_builder: DynamicPromptBuilder):
        self.profile = profile
        self.prompt_builder = prompt_builder
        self._spawned_specialists: Dict[str, DynamicSpecialistAgent] = {}
    
    def get_or_create(self, category: str) -> Optional[DynamicSpecialistAgent]:
        """
        Retorna especialista existente ou cria novo.
        
        Args:
            category: ID da categoria/dimensão de validação
        
        Returns:
            DynamicSpecialistAgent ou None se categoria inválida
        """
        # Se já criado, retorna
        if category in self._spawned_specialists:
            return self._spawned_specialists[category]
        
        # Procura dimensão no profile
        dimension = self.profile.get_dimension_by_id(category)
        if not dimension:
            logger.error(f"Categoria {category} não existe no DomainProfile")
            return None
        
        # Cria novo especialista
        specialist = DynamicSpecialistAgent(
            category=category,
            display_name=dimension.display_name,
            spawn_hint=dimension.spawn_hint,
            prompt_builder=self.prompt_builder
        )
        
        self._spawned_specialists[category] = specialist
        logger.info(f"[SpecialistFactory] Criado especialista: {specialist.display_name}")
        
        return specialist
    
    def get_spawned_categories(self) -> List[str]:
        """Retorna categorias já spawnadas."""
        return list(self._spawned_specialists.keys())
    
    def has_spawned(self, category: str) -> bool:
        """Verifica se categoria já foi spawnada."""
        return category in self._spawned_specialists
```

---

## 7. Módulo 6: `CategoryNormalizer` (Validação e Normalização)

### 7.1 Responsabilidade

Valida categorias novas vindo de respostas de LLM. Garante que categorias sejam do esquema dinâmico do domínio e evita rejeição de categorias legítimas.

### 7.2 Implementação

```python
# src/core/category_normalizer.py

import logging
from typing import Optional, List, Tuple

from src.core.domain_profile import DomainProfile

logger = logging.getLogger(__name__)

class CategoryNormalizer:
    """
    Normaliza categorias extraídas de respostas de LLM.
    Aceita categorias do esquema dinâmico do domínio.
    Rejeita ou mapeia categorias desconhecidas.
    """
    
    def __init__(self, profile: DomainProfile):
        self.profile = profile
        self._valid_category_ids = self.profile.get_dimension_ids()
        self._keyword_to_category_map = self._build_keyword_map()
    
    def normalize(self, raw_category: str) -> Optional[str]:
        """
        Normaliza categoria bruta para um ID válido.
        
        Algoritmo:
        1. Se ID válido, retornar como está
        2. Se não válido, procurar match via keywords
        3. Se nenhum match, retornar None (categoria desconhecida)
        """
        raw_upper = raw_category.strip().upper()
        
        # 1. Check se é ID válido
        if raw_upper in self._valid_category_ids:
            return raw_upper
        
        # 2. Procurar match via keywords
        for valid_id, keywords in self._keyword_to_category_map.items():
            if any(kw in raw_upper for kw in keywords):
                logger.debug(f"[CategoryNormalizer] Mapeado '{raw_category}' → '{valid_id}'")
                return valid_id
        
        # 3. Nenhum match — categoria desconhecida
        logger.warning(f"[CategoryNormalizer] Categoria desconhecida: '{raw_category}'")
        return None
    
    def _build_keyword_map(self) -> dict:
        """Constrói mapa de keywords para cada categoria."""
        keyword_map = {}
        for dimension in self.profile.validation_dimensions:
            keywords = dimension.keywords or self._extract_keywords_from_display_name(
                dimension.display_name
            )
            keyword_map[dimension.id] = keywords
        return keyword_map
    
    def _extract_keywords_from_display_name(self, name: str) -> List[str]:
        """Extrai keywords do nome para exibição."""
        # Ex: "Market Fit" → ["MARKET", "FIT"]
        return [word.upper() for word in name.split()]
```

---

## 8. Alterações no Core Existente

### 8.1 `ValidationBoard` — Evolução para Taxonomia Dinâmica

```python
# src/core/validation_board.py — MUDANÇAS

from src.core.domain_profile import DomainProfile

class ValidationBoard:
    
    def __init__(self, profile: Optional[DomainProfile] = None):
        # (código existente)
        self._profile = profile
        self._validation_schema = {}
        
        if profile:
            self.set_domain_profile(profile)
    
    def set_domain_profile(self, profile: DomainProfile) -> None:
        """
        Injeta DomainProfile dinâmico no board.
        Deve ser chamado após inicializar o board (no Round 0A).
        """
        self._profile = profile
        self._validation_schema = {
            dim.id: {
                "display_name": dim.display_name,
                "description": dim.description,
                "spawn_hint": dim.spawn_hint
            }
            for dim in profile.validation_dimensions
        }
        logger.info(f"[ValidationBoard] Injetado DomainProfile: {profile.domain}")
    
    def get_domain_profile(self) -> Optional[DomainProfile]:
        """Retorna o DomainProfile ativo."""
        return self._profile
    
    def get_validation_schema(self) -> Dict[str, Any]:
        """Retorna schema de validação (categorias dinâmicas)."""
        return self._validation_schema
    
    def is_valid_category(self, category: str) -> bool:
        """Verifica se categoria é válida no schema."""
        return category.upper() in self._validation_schema
    
    def get_open_issues_by_category(self) -> Dict[str, List[IssueRecord]]:
        """Agrupa issues abertos por categoria dinâmica."""
        by_category = {}
        for issue in self._issues.values():
            if issue.status == "OPEN":
                cat = issue.category.upper()
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(issue)
        return by_category
    
    def get_dominant_open_category(self) -> Optional[str]:
        """Retorna categoria com mais issues abertos."""
        by_cat = self.get_open_issues_by_category()
        if not by_cat:
            return None
        return max(by_cat.keys(), key=lambda k: len(by_cat[k]))
```

### 8.2 `AdaptiveOrchestrator` — Decisão com Categorias Dinâmicas

```python
# src/core/adaptive_orchestrator.py — MUDANÇAS

class AdaptiveOrchestrator:
    
    def __init__(self, ...):
        # (código existente)
        self._spawned_categories: set = set()
    
    def evaluate(self, ...):
        """
        Avaliação continua a mesma, mas agora pode trabalhar com
        categorias dinâmicas do ValidationBoard.
        """
        # Lógica existente de CONTINUE/STOP/SPAWN permanece idêntica
        # Mudança: usar board.get_dominant_open_category() em vez de
        # contar categorias fixas
        
        if round_num >= self._max_rounds:
            return OrchestratorDecision(action="STOP", reason="MAX_ROUNDS atingido")
        
        if round_num < self._min_rounds:
            return OrchestratorDecision(action="CONTINUE", reason="MIN_ROUNDS")
        
        # Verificar spawn
        dominant_category = self.board.get_dominant_open_category()
        if dominant_category and dominant_category not in self._spawned_categories: # Garante Deduplicação
            # Contar issues na categoria dominante
            open_by_cat = self.board.get_open_issues_by_category()
            if len(open_by_cat.get(dominant_category, [])) >= self._spawn_threshold:
                if self._current_agent_count < self._max_agents:
                    self._spawned_categories.add(dominant_category)
                    return OrchestratorDecision(
                        action="SPAWN",
                        reason=f"Lacuna em {dominant_category}",
                        category=dominant_category
                    )
        
        # Convergência
        if self.detector.has_converged(...):
            return OrchestratorDecision(action="STOP", reason="Convergência detectada")
        
        return OrchestratorDecision(action="CONTINUE", reason="Debate em andamento")
```

### 8.3 `DebateEngine` — Integração de Novos Módulos

```python
# src/debate/debate_engine.py — MUDANÇAS PRINCIPAIS

from src.core.domain_detector import DomainDetector
from src.core.domain_context_builder import DomainContextBuilder
from src.core.dynamic_prompt_builder import DynamicPromptBuilder
from src.agents.specialist_factory import SpecialistFactory

class DebateEngine:
    
    def __init__(self, provider, board, tracker, builder, ...):
        # (código existente)
        self.detector = DomainDetector()
        self.context_builder = DomainContextBuilder(provider)
        self.prompt_builder = None  # Criado após Round 0A
        self.specialist_factory = None  # Criado após Round 0A
    
    def run_debate(self, idea: str) -> DebateResult:
        """
        Novo fluxo com Round 0A (Meta-Orquestração) e 0B (Expansão).
        """
        
        # Nota: Round 0A (Meta-orquestração) agora ocorre no CONTROLLER.
        # O DebateEngine recebe o Board já injetado com o DomainProfile.
        logger.info("[DebateEngine] Engine inicializado. DomainProfile injetado previamente.")
        domain_profile = self.board.get_domain_profile()
        
        # Criar builders dinâmicos
        self.prompt_builder = DynamicPromptBuilder(self.board, domain_profile)
        self.specialist_factory = SpecialistFactory(domain_profile, self.prompt_builder)
        
        # ===== ROUND 0B: EXPANSÃO CONTEXTUALIZADA =====
        logger.info("[DebateEngine] Round 0B: Expansão")
        expansion_prompt = self.prompt_builder.build_expansion_prompt(idea)
        current_proposal = self.executor.proponent.expand(idea, expansion_prompt)
        self._log_round("proponent_expansion", current_proposal)
        
        # ===== ROUNDS 1+: DEBATE ADAPTATIVO =====
        current_round = 1
        last_defense = ""
        
        while current_round <= self.max_rounds:
            logger.info(f"[DebateEngine] Round {current_round}")
            
            # Crítica com categorias dinâmicas
            critique_prompt = self.prompt_builder.build_critique_prompt(
                current_proposal=current_proposal,
                last_defense=last_defense,
                open_issues=self.board.get_open_issues_for_critic_prompt(),
                validated_decisions=self.board.get_validated_decisions_prompt()
            )
            critic_result = self.executor.execute_critic_round(
                proposal_or_prompt=critique_prompt,
                ...
            )
            
            # Decisão de orquestração
            decision = self.orchestrator.evaluate(...)
            
            if decision.action == "SPAWN" and self.specialist_factory:
                logger.info(f"[DebateEngine] Spawning especialista para {decision.category}")
                specialist = self.specialist_factory.get_or_create(decision.category)
                if specialist:
                    spec_result = specialist.audit(
                        provider=self.provider,
                        proposal=current_proposal,
                        open_issues=self.board.get_open_issues_for_critic_prompt()
                    )
                    self._log_round(f"specialist_{decision.category}", spec_result)
                    # Extrair issues da resposta
                    self.tracker.extract_and_register_issues(spec_result, current_round, decision.category)
            
            if decision.action == "STOP":
                logger.info(f"[DebateEngine] STOP: {decision.reason}")
                break
            
            current_round += 1
        
        # Síntese (inalterada)
        return self._finalize_debate(current_proposal, ...)
```

### 8.4 `Controller` — Orquestração de Alto Nível

```python
# src/core/controller.py — MUDANÇAS MÍNIMAS

class Controller:
    
    def run(self, idea: str, model_name: str, ...):
        # (código existente)
        
        try:
            provider = self._get_provider(model_name, think)
            
            # === Round 0A: Meta-Orquestração ===
            detector = DomainDetector(...)
            domain_result = detector.detect(idea)
            cb = DomainContextBuilder(provider)
            profile = cb.build(idea, domain_result.domain)
            
            board = ValidationBoard()
            board.set_domain_profile(profile)
            builder = ContextBuilder(board)
            engine = DebateEngine(provider, board, self.tracker, builder)
        except ...:
            # (tratamento de erro)
            ...
        
        # DebateEngine cuida de Round 0B e adiante
        try:
            debate_result = engine.run_debate(idea)
        except ...:
            # (tratamento de erro)
            ...
        
        # Síntese e Relatório (inalterados)
        ...
```

---

## 9. Estratégia de Fallback e Robustez

### 9.1 Layers de Fallback

```
Camada 1: DomainDetector.detect()
├─ Se confidence < 50% → domain="generic"
└─ Nunca falha (100% programático)

Camada 2: DomainContextBuilder.build()
├─ Tenta LLM
├─ Se JSON inválido → extrai JSON ou aplica fallback
└─ Fallback determinístico por domínio sempre disponível

Camada 3: DebateEngine.run_debate()
├─ Se profile é None → usa profile genérico
└─ Debate continua com categorias universais
```

### 9.2 Garantias de Robustez

| Cenário | Comportamento |
|---|---|
| LLM não responde | Fallback para profile pré-configurado do domínio |
| JSON inválido | Extrator robusto tenta recuperar; se falhar, fallback |
| Domínio não reconhecido | DomainDetector retorna "generic" com fallback universal |
| Categoria inválida em issue | CategoryNormalizer mapeia ou marca como "GENERAL" |
| Especialista não pode ser criado | AdaptiveOrchestrator bloqueia spawn silenciosamente; continua debate |

---

## 10. Plano TDD — Testes Unitários e Integração

### 10.1 Sequência de Testes Unitários

#### Fase 1: DomainDetector

```python
# tests/unit/test_domain_detector.py

class TestDomainDetector:
    
    def test_detect_software_domain(self):
        """Detecta domínio software com keywords."""
        detector = DomainDetector()
        result = detector.detect("""
            Arquitetura backend com microservices, Kubernetes e segurança
        """)
        assert result.domain == "software"
        assert result.confidence >= 0.7
    
    def test_detect_business_domain(self):
        """Detecta domínio business com keywords."""
        idea = "Unit economics, market fit, go-to-market strategy"
        result = detector.detect(idea)
        assert result.domain == "business"
    
    def test_detect_philosophy_domain(self):
        """Detecta domínio philosophy."""
        idea = "Tese sobre lógica e epistemologia"
        result = detector.detect(idea)
        assert result.domain == "philosophy"
    
    def test_fallback_to_generic(self):
        """Idea genérica retorna domain='generic'."""
        idea = "Criar um novo projeto"
        result = detector.detect(idea)
        assert result.domain == "generic"
    
    def test_confidence_score(self):
        """Score de confiança está entre 0 e 1."""
        idea = "Qualquer ideia aqui"
        result = detector.detect(idea)
        assert 0.0 <= result.confidence <= 1.0
```

#### Fase 2: DomainProfile

```python
# tests/unit/test_domain_profile.py

class TestDomainProfile:
    
    def test_create_business_profile(self):
        """Cria profile com seções e dimensões."""
        profile = create_test_profile_business()
        assert profile.domain == "business"
        assert len(profile.expansion_sections) > 0
        assert len(profile.validation_dimensions) > 0
    
    def test_get_section_by_id(self):
        """Recupera seção pelo ID."""
        profile = create_test_profile_business()
        section = profile.get_section_by_id("PROBLEM_STATEMENT")
        assert section is not None
        assert section.id == "PROBLEM_STATEMENT"
    
    def test_get_dimension_by_id(self):
        """Recupera dimensão pelo ID."""
        profile = create_test_profile_business()
        dim = profile.get_dimension_by_id("MARKET_FIT")
        assert dim is not None
        assert dim.display_name == "Encaixe de Mercado"
```

#### Fase 3: DomainContextBuilder

```python
# tests/unit/test_domain_context_builder.py

class TestDomainContextBuilder:
    
    def test_build_with_fallback(self, mock_provider_fails):
        """Aplica fallback se LLM falha."""
        builder = DomainContextBuilder(mock_provider_fails)
        profile = builder.build("Ideia qualquer", "business")
        assert profile.source == "fallback"
        assert len(profile.expansion_sections) > 0
    
    def test_extract_json_from_response(self):
        """Extrai JSON de resposta com markdown."""
        builder = DomainContextBuilder(mock_provider)
        response = """
        Aqui está a análise:
        ```json
        {"expansion_sections": [...]}
        ```
        """
        data = builder._extract_json_from_response(response)
        assert "expansion_sections" in data
```

#### Fase 4: DynamicPromptBuilder

```python
# tests/unit/test_dynamic_prompt_builder.py

class TestDynamicPromptBuilder:
    
    def test_build_expansion_prompt(self):
        """Monta prompt de expansão com seções dinâmicas."""
        profile = create_test_profile_business()
        board = ValidationBoard(profile)
        builder = DynamicPromptBuilder(board, profile)
        
        prompt = builder.build_expansion_prompt("Ideia de negócio")
        assert "Problema ou Oportunidade" in prompt or "PROBLEM_STATEMENT" in prompt
        assert "domínio" in prompt.lower()
    
    def test_build_critique_prompt(self):
        """Monta prompt de crítica com categorias dinâmicas."""
        profile = create_test_profile_business()
        board = ValidationBoard(profile)
        builder = DynamicPromptBuilder(board, profile)
        
        prompt = builder.build_critique_prompt(
            current_proposal="Proposta",
            last_defense="Defesa",
            open_issues="",
            validated_decisions=""
        )
        assert "MARKET_FIT" in prompt or "Encaixe de Mercado" in prompt
    
    def test_build_specialist_prompt(self):
        """Monta prompt para especialista dinâmico."""
        profile = create_test_profile_business()
        board = ValidationBoard(profile)
        builder = DynamicPromptBuilder(board, profile)
        
        prompt = builder.build_specialist_prompt(
            category_id="MARKET_FIT",
            current_proposal="Proposta",
            open_issues=""
        )
        assert "Análise de Mercado" in prompt or "MARKET_FIT" in prompt
```

#### Fase 5: SpecialistFactory

```python
# tests/unit/test_specialist_factory.py

class TestSpecialistFactory:
    
    def test_create_specialist(self):
        """Factory cria especialista dinâmico."""
        profile = create_test_profile_business()
        builder = DynamicPromptBuilder(None, profile)
        factory = SpecialistFactory(profile, builder)
        
        specialist = factory.get_or_create("MARKET_FIT")
        assert specialist is not None
        assert specialist.category == "MARKET_FIT"
    
    def test_no_duplicate_spawn(self):
        """Factory não cria especialista duplicado."""
        profile = create_test_profile_business()
        builder = DynamicPromptBuilder(None, profile)
        factory = SpecialistFactory(profile, builder)
        
        s1 = factory.get_or_create("MARKET_FIT")
        s2 = factory.get_or_create("MARKET_FIT")
        assert s1 is s2
    
    def test_invalid_category_returns_none(self):
        """Factory retorna None para categoria inválida."""
        profile = create_test_profile_business()
        builder = DynamicPromptBuilder(None, profile)
        factory = SpecialistFactory(profile, builder)
        
        specialist = factory.get_or_create("INVALID_CATEGORY")
        assert specialist is None
```

#### Fase 6: CategoryNormalizer

```python
# tests/unit/test_category_normalizer.py

class TestCategoryNormalizer:
    
    def test_normalize_valid_category(self):
        """Normaliza categoria válida."""
        profile = create_test_profile_business()
        normalizer = CategoryNormalizer(profile)
        
        result = normalizer.normalize("MARKET_FIT")
        assert result == "MARKET_FIT"
    
    def test_normalize_keyword_match(self):
        """Mapeia categoria via keywords."""
        profile = create_test_profile_business()
        normalizer = CategoryNormalizer(profile)
        
        # Se "Mercado" é keyword de "MARKET_FIT"
        result = normalizer.normalize("Mercado")
        assert result == "MARKET_FIT" or result is None  # Depende de keywords
    
    def test_normalize_invalid_returns_none(self):
        """Categoria desconhecida retorna None."""
        profile = create_test_profile_business()
        normalizer = CategoryNormalizer(profile)
        
        result = normalizer.normalize("CATEGORIA_INEXISTENTE")
        assert result is None
```

#### Fase 7: ValidationBoard Evoluído

```python
# tests/unit/test_validation_board_evolved.py

class TestValidationBoardEvolved:
    
    def test_set_domain_profile(self):
        """Board carrega DomainProfile dinâmico."""
        profile = create_test_profile_business()
        board = ValidationBoard()
        board.set_domain_profile(profile)
        
        assert board.get_domain_profile() is profile
        assert board.is_valid_category("MARKET_FIT")
    
    def test_get_dominant_open_category(self):
        """Retorna categoria com mais issues abertos."""
        profile = create_test_profile_business()
        board = ValidationBoard()
        board.set_domain_profile(profile)
        
        # Adicionar issues
        board.add_issue(IssueRecord(
            issue_id="I1",
            severity="HIGH",
            category="MARKET_FIT",
            description="Issue 1"
        ))
        board.add_issue(IssueRecord(
            issue_id="I2",
            severity="MED",
            category="MARKET_FIT",
            description="Issue 2"
        ))
        board.add_issue(IssueRecord(
            issue_id="I3",
            severity="LOW",
            category="UNIT_ECONOMICS",
            description="Issue 3"
        ))
        
        dominant = board.get_dominant_open_category()
        assert dominant == "MARKET_FIT"
```

### 10.2 Testes de Integração

#### Integração 1: Detecção + BuilderContext

```python
# tests/integration/test_detection_and_build.py

def test_detect_and_build_domain_profile():
    """Full flow: detect → build → profile ready."""
    idea = "Marketplace de moda circular com unit economics de..."
    
    detector = DomainDetector()
    result = detector.detect(idea)
    assert result.domain == "business"
    
    mock_provider = MockProvider()
    builder = DomainContextBuilder(mock_provider)
    profile = builder.build(idea, result.domain)
    
    assert profile.domain == "business"
    assert len(profile.expansion_sections) > 0
    assert len(profile.validation_dimensions) > 0
```

#### Integração 2: Board + Orchestrator + Factory

```python
# tests/integration/test_board_orchestrator_factory.py

def test_spawn_specialist_from_board_state():
    """
    Full flow: Board tem issues → Orchestrator detecta lacuna →
    Factory cria especialista.
    """
    profile = create_test_profile_business()
    board = ValidationBoard()
    board.set_domain_profile(profile)
    
    # Adicionar issues
    for i in range(3):
        board.add_issue(IssueRecord(
            issue_id=f"I{i}",
            severity="MED",
            category="MARKET_FIT",
            description=f"Market issue {i}"
        ))
    
    # Orchestrator avalia
    orchestrator = AdaptiveOrchestrator(
        board=board,
        detector=ConvergenceDetector(),
        spawn_threshold=2
    )
    
    decision = orchestrator.evaluate(
        round_num=1,
        current_round_text="...",
        previous_round_text="...",
        new_issue_count=3
    )
    
    assert decision.action == "SPAWN"
    assert decision.category == "MARKET_FIT"
    
    # Factory cria especialista
    builder = DynamicPromptBuilder(board, profile)
    factory = SpecialistFactory(profile, builder)
    
    specialist = factory.get_or_create(decision.category)
    assert specialist is not None
    assert specialist.category == "MARKET_FIT"
```

#### Integração 3: Debate Completo com Onda 4.0

```python
# tests/integration/test_debate_full_onda4.py

def test_full_debate_flow_onda4():
    """
    Executa debate completo com Onda 4.0:
    Round 0A (detecção) → 0B (expansão) → 1+ (debate com especialistas).
    """
    idea = "Startup de marketplace B2B com foco em logística"
    
    provider = MockProvider()
    board = ValidationBoard()
    tracker = DebateStateTracker()
    builder = ContextBuilder(board)
    engine = DebateEngine(provider, board, tracker, builder)
    
    result = engine.run_debate(idea)
    
    assert result.status == "success"
    assert len(result.transcript) > 2  # Pelo menos Round 0B + Round 1
    assert result.board_snapshot is not None
    
    # Board deve ter DomainProfile injetado
    profile = board.get_domain_profile()
    assert profile is not None
    assert profile.domain == "business"
```

### 10.3 Testes de Domínios Específicos

```python
# tests/integration/test_domains_software_business_philosophy.py

class TestDomainsSupported:
    
    def test_software_domain_flow(self):
        """Onda 4.0 funciona para domínio software."""
        idea = "API REST escalável com autenticação OAuth2"
        # Executar debate e validar profile software
        ...
    
    def test_business_domain_flow(self):
        """Onda 4.0 funciona para domínio business."""
        idea = "SaaS com modelo freemium e expansão para enterprise"
        # Executar debate e validar profile business
        ...
    
    def test_philosophy_domain_flow(self):
        """Onda 4.0 funciona para domínio philosophy."""
        idea = "Tese sobre livre arbítrio e determinismo"
        # Executar debate e validar profile philosophy
        ...
```

---

## 11. Roadmap de Implementação

### Fase 1: Fundação (Semana 1)

- [ ] Criar `domain_detector.py` + testes unitários
- [ ] Criar `domain_profile.py` schema
- [ ] Criar `domain_context_builder.py` + fallbacks
- [ ] Criar `category_normalizer.py` + testes

**Critério de Aceite:** `pytest tests/unit/test_domain_* -v` passa (16+ testes)

### Fase 2: Builders e Factory (Semana 2)

- [ ] Criar `dynamic_prompt_builder.py`
- [ ] Criar `specialist_factory.py`
- [ ] Evolui `validation_board.py` para suportar profile dinâmico
- [ ] Testes unitários dos 3 módulos

**Critério de Aceite:** `pytest tests/unit/test_*builder* -v` passa (12+ testes)

### Fase 3: Integração no Core (Semana 3)

- [ ] Atualizar `adaptive_orchestrator.py` para categorias dinâmicas
- [ ] Atualizar `debate_engine.py` para Round 0A + 0B + specialist spawning
- [ ] Atualizar `controller.py` minimalmente
- [ ] Testes de integração

**Critério de Aceite:** Testes de integração passam; `pytest tests/integration/test_*.py -v` (8+ testes)

### Fase 4: Validação e Robustez (Semana 4)

- [ ] Testes de 3 domínios (software, business, philosophy)
- [ ] Testes de fallback (LLM failures, JSON inválido, etc.)
- [ ] Compatibilidade com Onda 3 (todos os 119 testes existentes passam)
- [ ] Documentação + exemplos

**Critério de Aceite:** 
- `pytest tests/ -v` → 100% sucesso (119 + 36 novos = 155+ testes)
- Smoke test: `python src/cli/main.py --idea "Ideia de negócio" --model gpt-oss:20b` → relatório gerado

---

## 12. Retrocompatibilidade e Migração da Onda 3

### 12.1 Garantias de Compatibilidade

| Componente | Onda 3 | Onda 4 | Status |
|---|---|---|---|
| `ValidationBoard` | Fixo `SECURITY, SCALABILITY, ...` | Dinâmico via `DomainProfile` | **Backward compatible**: Onda 4 suporta hardcoded profile se nenhum profile dinâmico injetado |
| `AdaptiveOrchestrator` | Categorias fixas | Categorias do board | **Backward compatible**: Lógica de spawn igual; apenas `category` é extraída dinamicamente |
| `DebateEngine` | Round 0 = expansão | Round 0A = meta + 0B = expansão | **Backward compatible**: Se ideal já expandida, pula Round 0 |
| `ContextBuilder` | Templates estáticos | Templates dinâmicos | **Backward compatible**: Inalterado se `DomainProfile` não injetado |
| `specialist_profiles.py` | Perfis fixos | Factory dinâmica | **Deprecado**: Mantém fallback para modo "classic" |

### 12.2 Modo de Compatibilidade (Default)

Todos os módulos novos têm defaults que restauram comportamento da Onda 3:

```python
# Exemplo: DynamicPromptBuilder com fallback

def __init__(self, board, profile: Optional[DomainProfile] = None):
    self.profile = profile or self._get_default_classic_profile()
```

Se nenhum `DomainProfile` é injetado, a Onda 4.0 executa como a Onda 3.

---

## 13. Checklist de Qualidade

### Antes de Marcar "Completo"

- [ ] **Cobertura de testes**: 85%+ de cobertura nos módulos novos
- [ ] **Testes existentes**: Todos os 119 testes da Onda 3 passam sem mudança
- [ ] **Testes de domínio**: Software + Business + Philosophy validados
- [ ] **Fallback**: Testado com LLM failures, JSON inválido, categoria desconhecida
- [ ] **Documentação**: Cada módulo tem docstring completo + exemplos
- [ ] **Performance**: Nenhuma degradação (Round 0A + 0B < 10s extra)
- [ ] **Segurança**: JSON parsing seguro, sem code injection via LLM
- [ ] **Linting**: `pylint` e `black` passam em todos os arquivos

---

## Conclusão

A **Onda 4.0** transforma o IdeaForge 2 em um motor universal de debate adversarial, agnóstico ao domínio, mantendo o rigor e a estrutura que o diferenciam. A arquitetura separa claramente a **estrutura invariante** (issues, decisões, fluxo programático) da **semântica mutável** (categorias, especialistas, prompts), permitindo que o sistema escale para qualquer domínio sem perder sua identidade.

Todos os módulos novos foram projetados para:
1. **Retrocompatibilidade total** com a Onda 3
2. **Robustez via fallbacks determinísticos**
3. **Testabilidade 100%**
4. **Compatibilidade com modelos pequenos**

Está pronto para implementação imediata.
