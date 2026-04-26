import pytest
import json
from src.agents.synthesizer_agent import SynthesizerAgent
from src.core.validation_board import ValidationBoard, IssueRecord
from tests.conftest import MockProvider

def test_synthesizer_has_all_sections():
    """Verifica se o relatório contém as 5 seções obrigatórias."""
    mock_response = (
        "# Sumário Executivo\nOK\n"
        "## Decisões Validadas\nD1\n"
        "## Issues Pendentes\nNenhum\n"
        "## Matriz de Risco\nBaixo\n"
        "## Veredito\nAprovado"
    )
    provider = MockProvider(responses={"synthesizer": mock_response})
    board = ValidationBoard()
    agent = SynthesizerAgent()
    
    result = agent.synthesize(board, "Teste Ideia", provider)
    
    assert result["status"] == "success"
    assert len(result["sections_present"]) == 5
    assert "# Sumário Executivo" in result["report_markdown"]
    assert "## Veredito" in result["report_markdown"]

def test_synthesizer_empty_board_no_hallucination():
    """Garante que seções vazias são marcadas como '(Nenhum registro) azul' conforme prompt."""
    # O mock provider deve retornar o que pedimos no prompt se o LLM for obediente
    mock_response = (
        "# Sumário Executivo\n(Nenhum registro)\n"
        "## Decisões Validadas\n(Nenhum registro)\n"
        "## Issues Pendentes\n(Nenhum registro)\n"
        "## Matriz de Risco\n(Nenhum registro)\n"
        "## Veredito\n(Nenhum registro)"
    )
    provider = MockProvider(responses={"synthesizer": mock_response})
    board = ValidationBoard()
    agent = SynthesizerAgent()
    
    result = agent.synthesize(board, "Vazio", provider)
    
    assert "(Nenhum registro)" in result["report_markdown"]

def test_synthesizer_returns_error_on_llm_exception():
    """Verifica comportamento quando o provedor LLM falha."""
    def error_gen(prompt):
        raise Exception("LLM Timeout")
        
    provider = MockProvider(responses=error_gen)
    board = ValidationBoard()
    agent = SynthesizerAgent()
    
    result = agent.synthesize(board, "Erro", provider)
    
    assert result["status"] == "error"
    assert "LLM Timeout" in result["error"]

def test_synthesizer_build_prompt_contains_snapshot():
    """Verifica se o prompt contém o snapshot JSON do board."""
    board = ValidationBoard()
    board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Desc"))
    
    agent = SynthesizerAgent()
    prompt = agent._build_prompt(board.snapshot(), "Snapshot Test")
    
    assert "ISS-01" in prompt
    assert "Snapshot Test" in prompt
    # Verifica se parece JSON
    assert '"issue_id": "ISS-01"' in prompt

def test_synthesizer_prompt_contains_use_data_instruction():
    """BUG-D: Verifica se o prompt contém a instrução de uso ativo dos dados (HF02)."""
    agent = SynthesizerAgent()
    prompt = agent._build_prompt({}, "Instruction Test")
    
    assert "USE esses dados para preencher as seções" in prompt
    assert "NUNCA deve gerar \"(Nenhum registro)\" em Issues ou Decisões" in prompt
