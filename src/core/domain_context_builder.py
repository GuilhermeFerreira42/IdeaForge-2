import json
import logging
import re
from typing import Optional, Dict, Any, List
from src.core.domain_profile import DomainProfile, ExpansionSection, ValidationDimension, ReportSection
from src.models.model_provider import ModelProvider

logger = logging.getLogger(__name__)

DOMAIN_CONTEXT_PROMPT = """
Você é um assistente de meta-análise do IdeaForge 2, especialista em decomposição de ideias complexas.

TAREFA: Analisar a ideia abaixo e retornar UM JSON estruturado que definirá o perfil de debate.
PROIBIDO: explicações fora do JSON. Se precisar falar algo, coloque dentro das instruções das seções.

IDEIA:
{idea}

DOMÍNIO DETECTADO: {detected_domain}

Retorne EXATAMENTE este JSON (UTF-8):

{{
  "expansion_sections": [
    {{
      "id": "SECAO_1_ID",
      "title": "Título em PT-BR",
      "instruction": "Instrução concisa (máx 160 chars)"
    }}
  ],
  "validation_dimensions": [
    {{
      "id": "DIMENSAO_1_ID",
      "display_name": "Nome para Exibição",
      "description": "Descrição breve do que valida",
      "spawn_hint": "Tipo de especialista"
    }}
  ],
  "specialist_hints": ["Especialista A", "Especialista B"],
  "critical_questions": ["Pergunta 1", "Pergunta 2"],
  "success_criteria": {{
    "criteria_1": "Descrição"
  }}
}}

REGRAS DE CONTEÚDO:
1. expansion_sections: 6-8 seções, IDs em UPPER_SNAKE_CASE, específicas para o domínio detectado
2. validation_dimensions: 4-6 dimensões cobrindo as principais lacunas desse tipo de ideia
3. specialist_hints: máx 3 especialistas mais prováveis para esse domínio
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
    },
    "hybrid": {
        "expansion_sections": [
            {"id": "PROPOSTA_VALOR", "title": "Proposta de Valor", "instruction": "Diferencial competitivo e dor resolvida"},
            {"id": "PUBLICO_CANAIS", "title": "Público e Canais", "instruction": "Segmentação e estratégia de aquisição"},
            {"id": "MODELO_RECEITA", "title": "Modelo de Receita", "instruction": "Como a solução gera faturamento"},
            {"id": "ARQUITETURA_TECNICA", "title": "Arquitetura Técnica", "instruction": "Componentes de software e infraestrutura"},
            {"id": "DADOS_INGESTAO", "title": "Stack de Dados e Ingestão", "instruction": "Origem, fluxo e processamento de dados"},
            {"id": "SEGURANCA_PRIVACIDADE", "title": "Segurança e Privacidade", "instruction": "Proteção de dados e conformidade"},
            {"id": "RISCOS_BARREIRAS", "title": "Riscos e Barreiras de Mercado", "instruction": "Desafios técnicos e competitivos"},
            {"id": "PREMISSAS_CRESCIMENTO", "title": "Premissas de Crescimento", "instruction": "Fatores críticos para escala"}
        ],
        "validation_dimensions": [
            {"id": "FEASIBILITY", "display_name": "Viabilidade Técnica", "description": "Capacidade de construir a solução", "spawn_hint": "Arquiteto de Soluções"},
            {"id": "BUSINESS_VIABILITY", "display_name": "Viabilidade de Negócio", "description": "Rentabilidade e mercado", "spawn_hint": "Analista de Negócios"},
            {"id": "SECURITY", "display_name": "Segurança", "description": "Riscos de dados e acesso", "spawn_hint": "Especialista em Segurança"}
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
        # max_tokens aumentado de 600 para 800 para evitar truncamento silencioso (W5Q-01)
        response = self.provider.generate(prompt=prompt, max_tokens=800, role="user")
        
        data = self._extract_json(response)
        if not data:
            raise ValueError("Não foi possível extrair JSON da resposta do LLM")
        
        return self._create_profile(data, detected_domain, "llm")

    def _extract_json(self, response: str) -> Optional[Dict[str, Any]]:
        # Caminho 1: Parse direto
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Caminho 2: Blocos de código Markdown
        match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Caminho 3: Boundary Detection (W5Q-01)
        # Captura o primeiro '{' e o último '}' para ignorar prosa ao redor
        try:
            start_idx = response.find('{')
            end_idx = response.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                json_str = response[start_idx:end_idx + 1]
                return json.loads(json_str)
        except Exception:
            pass
        
        return None

    def _apply_fallback(self, detected_domain: str) -> DomainProfile:
        fallback_data = DOMAIN_FALLBACKS.get(detected_domain, DOMAIN_FALLBACKS["generic"])
        return self._create_profile(fallback_data, detected_domain, "fallback")

    def _create_profile(self, data: Dict[str, Any], domain: str, source: str) -> DomainProfile:
        expansion_sections = [ExpansionSection(**s) for s in data.get("expansion_sections", [])]
        validation_dimensions = [ValidationDimension(**d) for d in data.get("validation_dimensions", [])]
        
        return DomainProfile(
            domain=data.get("domain", domain),
            confidence=1.0 if source == "llm" else 0.5,
            source=source,
            expansion_sections=expansion_sections,
            validation_dimensions=validation_dimensions,
            report_sections=[], # Será preenchido se necessário
            specialist_hints=data.get("specialist_hints", []),
            critical_questions=data.get("critical_questions", []),
            success_criteria=data.get("success_criteria", {})
        )
