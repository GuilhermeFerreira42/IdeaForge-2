import pytest
from src.agents import specialist_profiles

def test_get_profile_by_category():
    """Verifica se retorna o perfil correto para categorias conhecidas."""
    profile = specialist_profiles.get_profile("SECURITY")
    assert profile is not None
    assert profile["name"] == "SecurityAnalyst"
    assert "SECURITY" in profile["system_prompt"]

def test_get_profile_returns_none_for_unknown():
    """Verifica comportamento para categoria inexistente."""
    profile = specialist_profiles.get_profile("UNKNOWN_CAT")
    assert profile is None

def test_get_available_categories():
    """Garante que a lista de categorias disponíveis contém os especialistas base."""
    categories = specialist_profiles.get_available_categories()
    assert "SECURITY" in categories
    assert "SCALABILITY" in categories
    assert "FEASIBILITY" in categories

def test_build_specialist_prompt_replaces_placeholders():
    """Verifica a montagem de prompt com substituição de placeholders."""
    prompt = specialist_profiles.build_specialist_prompt(
        category="SECURITY",
        open_issues="ISS-01: Vazamento",
        current_proposal="Proposta X",
        last_defense="Defesa Y"
    )
    
    assert "{{CATEGORY}}" not in prompt
    assert "{{category}}" not in prompt.lower()
    assert "SECURITY" in prompt
    assert "ISS-01" in prompt
    assert "Proposta X" in prompt
    assert "Defesa Y" in prompt
