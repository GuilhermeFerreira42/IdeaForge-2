import pytest
from unittest.mock import MagicMock
from src.core.domain_context_builder import DomainContextBuilder, DOMAIN_FALLBACKS
from src.core.domain_profile import DomainProfile

def test_apply_fallback_for_generic():
    provider = MagicMock()
    builder = DomainContextBuilder(provider)
    profile = builder.build("Ideia vaga", "generic")
    
    assert profile.domain == "generic"
    assert profile.source == "fallback"
    # Verificar se as 7 seções universais estão lá
    section_ids = [s.id for s in profile.expansion_sections]
    expected = ["PROBLEMA", "PUBLICO_STAKEHOLDERS", "SOLUCAO_TESE", "OPERACAO_IMPLEMENTACAO", "RISCOS", "PREMISSAS", "CRITERIOS_SUCESSO"]
    for e in expected:
        assert e in section_ids

def test_build_with_llm_success():
    provider = MagicMock()
    # Mock return JSON valid match with contracts
    provider.generate.return_value = '{"expansion_sections": [{"id": "TEST", "title": "Test", "instruction": "Test"}], "validation_dimensions": [{"id": "DIM", "display_name": "Dim", "description": "Desc", "spawn_hint": "Hint"}]}'
    
    builder = DomainContextBuilder(provider)
    profile = builder.build("SaaS de Logística", "business")
    
    assert profile.source == "llm"
    assert profile.get_section_by_id("TEST").title == "Test"

def test_extract_json_from_markdown():
    provider = MagicMock()
    # Mock MD wrapped JSON
    provider.generate.return_value = 'Aqui está o JSON:\n```json\n{"expansion_sections": [], "validation_dimensions": []}\n```'
    builder = DomainContextBuilder(provider)
    profile = builder.build("Ideia", "software")
    assert profile.source == "llm"
