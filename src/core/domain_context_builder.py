import json
import logging
import re
from typing import Optional, Dict, Any, List
from src.core.domain_profile import DomainProfile, ExpansionSection, ValidationDimension, ReportSection
from src.models.model_provider import ModelProvider

logger = logging.getLogger(__name__)

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

DOMAIN_FALLBACKS = {
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
            {"id": "FEASIBILITY", "display_name": "Viabilidade", "description": "Capacidade técnica e operacional de executar a ideia", "spawn_hint": "Especialista em Viabilidade"},
            {"id": "COMPLETENESS", "display_name": "Completude", "description": "Se a proposta cobre todos os aspectos necessários", "spawn_hint": "Especialista em Análise de Sistemas"},
            {"id": "CONSISTENCY", "display_name": "Consistência", "description": "Ausência de contradições internas", "spawn_hint": "Especialista em Lórica"},
            {"id": "RISK_ASSESSMENT", "display_name": "Avaliação de Riscos", "description": "Identificação e mitigação de riscos críticos", "spawn_hint": "Especialista em Gestão de Riscos"}
        ]
    },
    "software": {
        "expansion_sections": [
            {"id": "OVERVIEW", "title": "Visão Geral", "instruction": "Resumo técnico da solução"},
            {"id": "ARCHITECTURE", "title": "Arquitetura", "instruction": "Componentes principais e stack"},
            {"id": "SECURITY", "title": "Segurança", "instruction": "Protocolos e medidas de proteção"},
            {"id": "DATABASE", "title": "Banco de Dados", "instruction": "Modelagem e persistência"},
            {"id": "API", "title": "Interface/API", "instruction": "Endpoints e integração"},
            {"id": "INFRA", "title": "Infraestrutura", "instruction": "Deploy e cloud"}
        ],
        "validation_dimensions": [
            {"id": "SECURITY", "display_name": "Segurança", "description": "Vulnerabilidades e ataques", "spawn_hint": "Especialista em Segurança Cibernética"},
            {"id": "SCALABILITY", "display_name": "Escalabilidade", "description": "Performance sob carga", "spawn_hint": "Engenheiro de SRE"},
            {"id": "RELIABILITY", "display_name": "Confiabilidade", "description": "Disponibilidade e tolerância a falhas", "spawn_hint": "Arquiteto de Sistemas"}
        ]
    }
}

class DomainContextBuilder:
    def __init__(self, provider: ModelProvider):
        self.provider = provider

    def build(self, idea: str, detected_domain: str) -> DomainProfile:
        try:
            return self._build_with_llm(idea, detected_domain)
        except Exception as e:
            logger.warning(f"LLM falhou no DomainContextBuilder: {e}. Aplicando fallback...")
            return self._apply_fallback(detected_domain)

    def _build_with_llm(self, idea: str, detected_domain: str) -> DomainProfile:
        prompt = DOMAIN_CONTEXT_PROMPT.format(idea=idea[:800], detected_domain=detected_domain)
        response = self.provider.generate(prompt=prompt, max_tokens=600, role="user")
        
        data = self._extract_json(response)
        if not data:
            raise ValueError("Não foi possível extrair JSON da resposta do LLM")
        
        return self._create_profile(data, detected_domain, "llm")

    def _extract_json(self, response: str) -> Optional[Dict[str, Any]]:
        # Tenta parse direto
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Tenta extrair de blocos de código
        match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        return None

    def _apply_fallback(self, detected_domain: str) -> DomainProfile:
        fallback_data = DOMAIN_FALLBACKS.get(detected_domain, DOMAIN_FALLBACKS["generic"])
        return self._create_profile(fallback_data, detected_domain, "fallback")

    def _create_profile(self, data: Dict[str, Any], domain: str, source: str) -> DomainProfile:
        expansion_sections = [ExpansionSection(**s) for s in data.get("expansion_sections", [])]
        validation_dimensions = [ValidationDimension(**d) for d in data.get("validation_dimensions", [])]
        
        return DomainProfile(
            domain=domain,
            confidence=1.0 if source == "llm" else 0.5,
            source=source,
            expansion_sections=expansion_sections,
            validation_dimensions=validation_dimensions,
            report_sections=[], # Será preenchido se necessário
            specialist_hints=data.get("specialist_hints", []),
            critical_questions=data.get("critical_questions", []),
            success_criteria=data.get("success_criteria", {})
        )
