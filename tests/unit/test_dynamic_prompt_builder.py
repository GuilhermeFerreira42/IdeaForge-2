import pytest
from src.core.domain_profile import DomainProfile, ExpansionSection, ValidationDimension
from src.core.dynamic_prompt_builder import DynamicPromptBuilder
from src.core.validation_board import ValidationBoard

@pytest.fixture
def sample_profile():
    return DomainProfile(
        domain="software",
        confidence=1.0,
        source="manual",
        expansion_sections=[
            ExpansionSection(id="ARCH", title="Arquitetura", instruction="Defina componentes")
        ],
        validation_dimensions=[
            ValidationDimension(id="SEC", display_name="Segurança", description="Desc", spawn_hint="Expert")
        ],
        report_sections=[]
    )

def test_build_expansion_prompt_includes_sections(sample_profile):
    board = ValidationBoard(profile=sample_profile)
    builder = DynamicPromptBuilder(board, sample_profile)
    prompt = builder.build_expansion_prompt("Ideia teste")
    
    assert "Arquitetura" in prompt
    assert "ESTRUTURA OBRIGATÓRIA" in prompt
    assert "1. Arquitetura" in prompt

def test_build_specialist_prompt_enforces_table_contract(sample_profile):
    board = ValidationBoard(profile=sample_profile)
    builder = DynamicPromptBuilder(board, sample_profile)
    prompt = builder.build_specialist_prompt(
        category="SEC",
        idea="SaaS de Banco",
        current_proposal="# 1. Arq",
        open_issues="Nenhum"
    )
    
    assert "| Severidade | Categoria |" in prompt
    assert "Segurança" in prompt
    assert "PROIBIDO: introduções" in prompt

def test_fallback_to_generic_if_no_profile():
     board = ValidationBoard()
     builder = DynamicPromptBuilder(board)
     prompt = builder.build_expansion_prompt("Ideia")
     assert "Problema" in prompt # Generic fallback section
