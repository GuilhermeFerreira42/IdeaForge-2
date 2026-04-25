import pytest
from src.agents.proponent_agent import ProponentAgent
from tests.conftest import MockProvider

def test_expansion_generates_7_sections():
    """Verifica se o modo expansão produz as 7 seções obrigatórias."""
    mock_response = (
        "# 1. Visão Geral\nConteúdo...\n"
        "# 2. Arquitetura de Componentes\nConteúdo...\n"
        "# 3. Fluxo de Dados Principal\nConteúdo...\n"
        "# 4. Stack Tecnológica Sugerida\nConteúdo...\n"
        "# 5. Principais Desafios Técnicos\nConteúdo...\n"
        "# 6. Premissas de Implementação\nConteúdo...\n"
        "# 7. Próximos Passos Imediatos\nConteúdo..."
    )
    provider = MockProvider(responses={"proponent": mock_response})
    agent = ProponentAgent(provider=provider)
    
    result = agent.expand("Ideia de teste")
    
    assert "# 1. Visão Geral" in result
    assert "# 7. Próximos Passos Imediatos" in result
    # Contar seções (headings de nível 1 ou similar)
    sections = [line for line in result.split('\n') if line.strip().startswith('# ')]
    assert len(sections) >= 7

def test_expansion_sections_non_empty():
    """Garante que as seções da expansão não são vazias."""
    mock_response = (
        "# 1. Visão Geral\n" + "x" * 50 + "\n"
        "# 2. Seção\n" + "y" * 50 + "\n"
        "# 3. Seção\n" + "y" * 50 + "\n"
        "# 4. Seção\n" + "y" * 50 + "\n"
        "# 5. Seção\n" + "y" * 50 + "\n"
        "# 6. Seção\n" + "y" * 50 + "\n"
        "# 7. Seção\n" + "y" * 50
    )
    provider = MockProvider(responses={"proponent": mock_response})
    agent = ProponentAgent(provider=provider)
    
    result = agent.expand("Ideia de teste")
    
    parts = result.split('# ')
    for part in parts[1:]: # Ignora o que vem antes do primeiro #
        content = part.split('\n', 1)[1] if '\n' in part else ""
        assert len(content.strip()) >= 20

def test_defense_references_issues():
    """Verifica se o modo defesa referencia IDs de issues no formato ISS-XX."""
    mock_response = (
        "## Pontos Aceitos\n- Aceito ISS-01 e ISS-02.\n"
        "## Defesa Técnica\nJustificativa...\n"
        "## Melhorias Propostas\n| Seção | Mudança | Justificativa |"
    )
    provider = MockProvider(responses={"proponent": mock_response})
    agent = ProponentAgent(provider=provider)
    
    # Simular contextBuilder montando o prompt
    prompt = "Prompt com ISS-01 e ISS-02 abertos"
    result = agent.defend(prompt)
    
    assert "ISS-01" in result
    assert "ISS-02" in result

def test_defense_has_3_sections():
    """Garante que a defesa contém as 3 seções obrigatórias."""
    mock_response = (
        "## Pontos Aceitos\n...\n"
        "## Defesa Técnica\n...\n"
        "## Melhorias Propostas\n..."
    )
    provider = MockProvider(responses={"proponent": mock_response})
    agent = ProponentAgent(provider=provider)
    
    result = agent.defend("Prompt de defesa")
    
    assert "## Pontos Aceitos" in result
    assert "## Defesa Técnica" in result
    assert "## Melhorias Propostas" in result

def test_agent_uses_correct_templates():
    """Verifica se o agente inclui os templates do prompt_templates no prompt final."""
    from src.core import prompt_templates
    provider = MockProvider(responses={"proponent": "ok"})
    agent = ProponentAgent(provider=provider)
    
    agent.expand("Ideia")
    last_prompt = provider.call_log[0]["prompt"]
    # Nota: mock provider trunca em 200 chars no log, mas vamos testar partes
    assert "Agente Proponente" in last_prompt or "ESTRUTURA OBRIGATÓRIA" in last_prompt
