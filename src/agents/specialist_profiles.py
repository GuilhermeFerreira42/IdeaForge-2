from typing import Dict, Any, List, Optional
from src.core import prompt_templates

SPECIALIST_PROFILES = {
    "SECURITY": {
        "name": "SecurityAnalyst",
        "role": "security_analyst",
        "system_prompt": (
            "Você é um Analista de Segurança especializado.\n\n"
            "TAREFA: Avaliar a proposta focando EXCLUSIVAMENTE em:\n"
            "- Vulnerabilidades de autenticação e autorização\n"
            "- Exposição de dados sensíveis\n"
            "- Superfície de ataque\n"
            "- Validação de inputs\n\n"
            "REGRAS:\n"
            "1. NÃO gerar ID de issue.\n"
            "2. Tabela com EXATAMENTE 4 colunas: Severidade | Categoria | Descrição | Sugestão\n"
            "3. Severidade: APENAS HIGH, MED ou LOW\n"
            "4. Categoria: SEMPRE 'SECURITY'\n"
            "5. Sugestão de mitigação CONCRETA para cada issue\n"
            "6. PROIBIDO repetir issues já listados: {{OPEN_ISSUES}}\n"
            "7. Responda em Português\n"
            "8. Máximo 300 palavras\n"
        )
    },
    "SCALABILITY": {
        "name": "ScalabilityExpert",
        "role": "scalability_expert",
        "system_prompt": (
            "Você é um Especialista em Escalabilidade e Performance.\n\n"
            "TAREFA: Avaliar a capacidade da proposta de suportar crescimento.\n"
            "FOCO: Gargalos de I/O, latência, concorrência, limites de banco de dados.\n\n"
            "REGRAS:\n"
            "1. Tabela de 4 colunas.\n"
            "2. Categoria: SEMPRE 'SCALABILITY'.\n"
            "3. PROIBIDO repetir issues: {{OPEN_ISSUES}}\n"
        )
    },
    "FEASIBILITY": {
        "name": "TechLead",
        "role": "tech_lead",
        "system_prompt": (
            "Você é um Tech Lead focado em Viabilidade Técnica.\n\n"
            "TAREFA: Avaliar se a proposta é realizável no tempo e recursos dados.\n"
            "FOCO: Anti-patterns, complexidade desnecessária, tech stack inadequada.\n\n"
            "REGRAS:\n"
            "1. Tabela de 4 colunas.\n"
            "2. Categoria: SEMPRE 'FEASIBILITY'.\n"
            "3. PROIBIDO repetir issues: {{OPEN_ISSUES}}\n"
        )
    },
    "COMPLETENESS": {
        "name": "ProductArchitect",
        "role": "product_architect",
        "system_prompt": (
            "Você é um Arquiteto de Produto focado em completude.\n\n"
            "TAREFA: Identificar seções ou detalhes cruciais ausentes.\n"
            "FOCO: Edge cases não tratados, lacunas na lógica de negócio.\n\n"
            "REGRAS:\n"
            "1. Tabela de 4 colunas.\n"
            "2. Categoria: SEMPRE 'COMPLETENESS'.\n"
            "3. PROIBIDO repetir issues: {{OPEN_ISSUES}}\n"
        )
    }
}

def get_profile(category: str) -> Optional[Dict[str, Any]]:
    """Retorna o perfil do especialista para a categoria informada."""
    return SPECIALIST_PROFILES.get(category.upper())

def get_available_categories() -> List[str]:
    """Retorna a lista de categorias que possuem especialistas configurados."""
    return list(SPECIALIST_PROFILES.keys())

def build_specialist_prompt(
    category: str,
    open_issues: str,
    current_proposal: str,
    last_defense: str
) -> str:
    """
    Monta o prompt completo para um especialista.
    """
    profile = get_profile(category)
    if not profile:
        # Fallback para base prompt se categoria for desconhecida mas válida no sistema
        base = prompt_templates.SPECIALIST_BASE_PROMPT
        system = base.replace("{{CATEGORY}}", category)
    else:
        system = profile["system_prompt"]
        
    # Replaçar placeholders comuns
    prompt = f"{system}\n\n"
    prompt += f"ISSUES ABERTOS:\n{open_issues}\n\n"
    prompt += f"PROPOSTA VIGENTE:\n{current_proposal}\n\n"
    prompt += f"ÚLTIMA DEFESA DO PROPONENTE:\n{last_defense}\n\n"
    
    # Garantir que placeholders do template de specialist_base também sejam limpos caso usados
    prompt = prompt.replace("{{OPEN_ISSUES}}", open_issues)
    prompt = prompt.replace("{{CATEGORY}}", category)
    
    return prompt
