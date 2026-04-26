import logging
from typing import Optional, List
from src.core.domain_profile import DomainProfile, ExpansionSection
from src.core.validation_board import ValidationBoard

logger = logging.getLogger(__name__)

# Contrato Invariante de Formatação
ISSUE_TABLE_HEADER = "| Severidade | Categoria | Descrição | Sugestão |"
ISSUE_TABLE_SEPARATOR = "|------------|-----------|-----------|-----------|"

EXPANSION_SYSTEM_PROMPT = """
Você é o Agente Proponente do IdeaForge 2, atuando no domínio: {domain}.

Sua missão é expandir uma ideia bruta em uma proposta estruturada e técnica.

ESTRUTURA OBRIGATÓRIA ({section_count} Seções numeradas):
{sections_str}

REGRAS RÍGIDAS:
1. Use EXATAMENTE as seções numeradas acima.
2. Seja técnico, direto e detalhado em cada seção.
3. PROIBIDO: introduções genéricas, saudações ou conclusões narrativas.
4. FOCO: Viabilidade e clareza.
"""

SPECIALIST_SYSTEM_PROMPT = """
Você é um Especialista em {display_name} (Categoria: {category}).
Sua missão é atuar como Crítico Técnico no domínio {domain}.

TAREFA: Avaliar a proposta focando EXCLUSIVAMENTE em problemas de {display_name}.

CONTRATO DE RESPOSTA:
1. Sua crítica deve ser entregue EXCLUSIVAMENTE em uma tabela Markdown.
2. A tabela deve ter EXATAMENTE as colunas do cabeçalho abaixo:
{table_header}
{table_separator}

REGRAS:
- Severidade: HIGH, MED ou LOW.
- Categoria: SEMPRE '{category}'.
- Sugestão: Mitigação técnica concreta para o problema.
- PROIBIDO: introduções, explicações fora da tabela ou saudações.
- PROIBIDO: repetir issues já listados em 'ISSUES ABERTOS'.

DOMÍNIO: {domain}
"""

class DynamicPromptBuilder:
    """
    Construtor dinâmico de prompts que garante contratos invariantes.
    Injeta configurações do DomainProfile em templates de sistema.
    """
    def __init__(self, board: ValidationBoard, profile: Optional[DomainProfile] = None):
        self.board = board
        # Se profile não fornecido, usa o injetado no board, ou fallback genérico
        self.profile = profile or board.get_domain_profile()
        if not self.profile:
            # Fallback genérico de segurança (deve bater com o DomainContextBuilder)
            from src.core.domain_context_builder import DOMAIN_FALLBACKS
            from src.core.domain_context_builder import DomainContextBuilder
            # Dummy provider apenas para criar o profile de fallback
            self.profile = DomainContextBuilder(None)._apply_fallback("generic")

    def build_expansion_prompt(self, idea: str) -> str:
        sections_str = "\n".join([f"{i+1}. {s.title}" for i, s in enumerate(self.profile.expansion_sections)])
        
        system = EXPANSION_SYSTEM_PROMPT.format(
            domain=self.profile.domain.upper(),
            section_count=len(self.profile.expansion_sections),
            sections_str=sections_str
        )
        
        return f"{system}\n\nIDEIA BRUTA:\n{idea}\n\nGERAR AGORA:"

    def build_specialist_prompt(self, category: str, idea: str, current_proposal: str, open_issues: str) -> str:
        # Tenta achar a dimensão no profile
        dim = self.profile.get_dimension_by_id(category)
        display_name = dim.display_name if dim else category
        
        system = SPECIALIST_SYSTEM_PROMPT.format(
            display_name=display_name,
            category=category.upper(),
            domain=self.profile.domain.upper(),
            table_header=ISSUE_TABLE_HEADER,
            table_separator=ISSUE_TABLE_SEPARATOR
        )
        
        prompt = f"{system}\n\n"
        prompt += f"IDEIA ORIGINAL: {idea}\n\n"
        prompt += f"ISSUES ABERTOS:\n{open_issues}\n\n"
        prompt += f"PROPOSTA VIGENTE:\n{current_proposal}\n\n"
        prompt += "GERAR TABELA DE CRÍTICA AGORA:"
        
        return prompt
