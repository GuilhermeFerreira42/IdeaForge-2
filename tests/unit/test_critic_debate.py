import pytest
from src.agents.critic_agent import CriticAgent
from tests.conftest import MockProvider

def test_critique_generates_issues():
    """Verifica se a crítica produz pelo menos uma linha de issue em tabela."""
    mock_response = (
        "## Novos Issues Encontrados\n"
        "| Severidade | Categoria | Descrição | Sugestão |\n"
        "|---|---|---|---|\n"
        "| HIGH | SECURITY | Falha grave | Corrigir agora |"
    )
    provider = MockProvider(responses={"critic": mock_response})
    agent = CriticAgent(provider=provider)
    
    result = agent.review("Prompt montado")
    
    assert "HIGH" in result
    assert "SECURITY" in result
    assert "|" in result

def test_critique_respects_4_columns():
    """Garante que a tabela de issues tem exatamente 4 colunhas."""
    mock_response = (
        "| HIGH | SECURITY | Desc | Sug |"
    )
    provider = MockProvider(responses={"critic": mock_response})
    agent = CriticAgent(provider=provider)
    
    result = agent.review("Prompt")
    
    lines = [l for l in result.split('\n') if '|' in l]
    for line in lines:
        cols = [c.strip() for c in line.split('|') if c.strip()]
        assert len(cols) == 4

def test_critique_status_resolved_marker():
    """Verifica se o Critic consegue marcar resoluções com ✅ ou ❌."""
    mock_response = (
        "## Avaliação de Resoluções\n"
        "- ISS-01: ✅ RESOLVED\n"
        "- ISS-02: ❌ MANTER OPEN"
    )
    provider = MockProvider(responses={"critic": mock_response})
    agent = CriticAgent(provider=provider)
    
    result = agent.review("Prompt")
    
    assert "✅" in result
    assert "❌" in result
    assert "ISS-01" in result

def test_no_id_extraction_in_critique():
    """Garante que o Critic não tenta gerar IDs novos (ex: ISS-99)."""
    mock_response = (
        "| HIGH | SECURITY | Problema | Solução |"
    )
    provider = MockProvider(responses={"critic": mock_response})
    agent = CriticAgent(provider=provider)
    
    result = agent.review("Prompt")
    
    # Não deve ter ISS- seguido de números na parte de novos issues
    assert "ISS-" not in result.split("Novos Issues Encontrados")[-1]
