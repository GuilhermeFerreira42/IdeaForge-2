from src.models.model_provider import ModelProvider
from src.core import prompt_templates

class ProponentAgent:
    """
    Agente Proponente v2.
    Responsável por expandir a ideia inicial e defendê-la durante o debate.
    """

    def __init__(self, provider: ModelProvider):
        self.provider = provider

    def expand(self, idea: str) -> str:
        """
        Modo Expansão (Round 0): Transforma ideia bruta em proposta de 7 seções.
        """
        prompt = (
            f"{prompt_templates.EXPANSION_SYSTEM_PROMPT}\n\n"
            f"IDEIA BRUTA:\n{idea}\n\n"
            "Gere a proposta estruturada seguindo rigorosamente as 7 seções."
        )
        
        response = self.provider.generate(prompt=prompt, role="proponent")
        return response

    def defend(self, context_prompt: str) -> str:
        """
        Modo Defesa: Responde a críticas e propõe patches.
        O contexto completo (proposta + issues + crítica) é montado pelo ContextBuilder.
        """
        # O context_prompt já vem com o system prompt e placeholders preenchidos 
        # pelo ContextBuilder, mas por segurança, se vier apenas o corpo, 
        # o agente garante o system prompt.
        
        if "Você é o Agente Proponente defendendo sua proposta" not in context_prompt:
             prompt = f"{prompt_templates.DEFENSE_SYSTEM_PROMPT}\n\n{context_prompt}"
        else:
             prompt = context_prompt

        response = self.provider.generate(prompt=prompt, role="proponent")
        return response
