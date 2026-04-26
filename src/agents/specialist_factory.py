import logging
from typing import Optional
from src.core.domain_profile import DomainProfile
from src.core.dynamic_prompt_builder import DynamicPromptBuilder
from src.models.model_provider import ModelProvider

logger = logging.getLogger(__name__)

class DynamicSpecialistAgent:
    """
    Agente especialista criado dinamicamente para uma categoria específica.
    Encapsula o comportamento de crítica usando prompts dinâmicos.
    """
    def __init__(self, category: str, builder: DynamicPromptBuilder, provider: ModelProvider):
        self.category = category
        self.builder = builder
        self.provider = provider

    def act(self, idea: str, current_proposal: str, open_issues: str) -> str:
        """Executa a crítica especializada."""
        prompt = self.builder.build_specialist_prompt(
            category=self.category,
            idea=idea,
            current_proposal=current_proposal,
            open_issues=open_issues
        )
        logger.info(f"[DynamicSpecialist] Executando crítica para categoria: {self.category}")
        return self.provider.generate(prompt=prompt, role="specialist")

class SpecialistFactory:
    """
    Fábrica responsável por instanciar especialistas on-the-fly.
    Garante que cada especialista use o contexto dinâmico do domínio atual.
    """
    def __init__(self, profile: DomainProfile, builder: DynamicPromptBuilder, provider: Optional[ModelProvider] = None):
        self.profile = profile
        self.builder = builder
        self.provider = provider # Pode ser injetado depois ou no engine

    def create_specialist(self, category: str, provider: Optional[ModelProvider] = None) -> DynamicSpecialistAgent:
        """
        Cria uma instância de um especialista para a categoria informada.
        """
        active_provider = provider or self.provider
        if not active_provider:
            raise ValueError("Fábrica precisa de um ModelProvider para instanciar especialistas.")
            
        logger.info(f"[SpecialistFactory] Criando novo especialista: {category}")
        return DynamicSpecialistAgent(
            category=category.upper(),
            builder=self.builder,
            provider=active_provider
        )
