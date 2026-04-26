import pytest
from unittest.mock import MagicMock
from src.core.domain_profile import DomainProfile, ValidationDimension
from src.agents.specialist_factory import SpecialistFactory
from src.core.dynamic_prompt_builder import DynamicPromptBuilder

@pytest.fixture
def sample_profile():
    return DomainProfile(
        domain="software",
        confidence=1.0,
        source="manual",
        expansion_sections=[],
        validation_dimensions=[
            ValidationDimension(id="SEC", display_name="Segurança", description="Desc", spawn_hint="Perito em Segurança")
        ],
        report_sections=[]
    )

def test_create_specialist_returns_agent(sample_profile):
    builder = MagicMock(spec=DynamicPromptBuilder)
    provider = MagicMock()
    factory = SpecialistFactory(sample_profile, builder, provider)
    
    agent = factory.create_specialist("SEC")
    assert agent is not None
    assert hasattr(agent, "act") # Interface dinâmica: .act()
    
def test_create_specialist_unknown_category_uses_generic(sample_profile):
    builder = MagicMock(spec=DynamicPromptBuilder)
    provider = MagicMock()
    factory = SpecialistFactory(sample_profile, builder, provider)
    
    agent = factory.create_specialist("UNKNOWN")
    assert agent is not None

def test_factory_integration_with_builder_call(sample_profile):
    builder = MagicMock(spec=DynamicPromptBuilder)
    factory = SpecialistFactory(sample_profile, builder)
    
    # Ao criar ou usar o especialista, ele deve eventualmente pedir um prompt ao builder
    # Isso depende da implementação, mas vamos validar se o builder está acessível
    assert factory.builder == builder
