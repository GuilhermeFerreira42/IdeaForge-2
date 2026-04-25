from src.models.model_provider import ModelProvider
from src.core import prompt_templates

class CriticAgent:
    """
    Agente Crítico v2.
    Responsável por auditar propostas técnicas e levantar issues estruturadas.
    """

    def __init__(self, provider: ModelProvider):
        self.provider = provider

    def review(self, context_prompt: str) -> str:
        """
        Analisa a proposta e gera crítica estruturada.
        O prompt completo (proposta + última defesa + issues abertos) 
        é montado pelo ContextBuilder.
        """
        # O context_prompt já vem com o system prompt e placeholders preenchidos
        if "Você é o Agente Crítico do sistema IdeaForge 2" not in context_prompt:
             prompt = f"{prompt_templates.CRITIQUE_SYSTEM_PROMPT}\n\n{context_prompt}"
        else:
             prompt = context_prompt

        response = self.provider.generate(prompt=prompt, role="critic")
        return response
