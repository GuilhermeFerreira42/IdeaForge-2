import pytest
from src.debate.round_executor import RoundExecutor, RoundResult
from src.core.validation_board import ValidationBoard
from src.debate.debate_state_tracker import DebateStateTracker
from src.debate.context_builder import ContextBuilder
from tests.conftest import MockProvider

def test_execute_critic_round_success():
    """Verifica a execução de um round de crítica com extração de issues."""
    board = ValidationBoard()
    tracker = DebateStateTracker()
    builder = ContextBuilder(board=board)
    
    mock_response = (
        "## Novos Issues Encontrados\n"
        "| HIGH | SECURITY | Falha | Corrigir |"
    )
    provider = MockProvider(responses={"critic": mock_response})
    executor = RoundExecutor(provider=provider, board=board, tracker=tracker, builder=builder)
    
    result = executor.execute_critic_round(current_proposal="P1", last_defense="D1", round_num=1)
    
    assert isinstance(result, RoundResult)
    assert result.new_issue_count == 1
    assert result.parsing_succeeded is True
    assert "Falha" in result.raw_text

def test_execute_critic_round_parsing_failure_detection():
    """Verifica detecção de subextração (COR-14)."""
    board = ValidationBoard()
    tracker = DebateStateTracker()
    builder = ContextBuilder(board=board)
    
    # Resposta longa mas sem tabela detectável pelo tracker
    # 'problema' está na lista de detecção do RoundExecutor mas não é keyword do Tracker L3
    mock_response = (
        "Esta proposta tem um grande problema estrutural. "
        "Não ficou claro como escalar. " + "x" * 300
    )
    provider = MockProvider(responses={"critic": mock_response})
    executor = RoundExecutor(provider=provider, board=board, tracker=tracker, builder=builder)
    
    result = executor.execute_critic_round(current_proposal="P1", last_defense="D1", round_num=1)
    
    # Resposta substancial (>200 chars) mas 0 issues extraídos -> parsing_succeeded=False
    assert result.new_issue_count == -1
    assert result.parsing_succeeded is False

def test_execute_defense_round_with_patches():
    """Verifica round de defesa com aplicação de patches na proposta."""
    board = ValidationBoard()
    tracker = DebateStateTracker()
    builder = ContextBuilder(board=board)
    
    proposal = "## Visão Geral\nOriginal\n## Stack\nPython"
    mock_response = (
         "## Melhorias Propostas\n"
         "| Visão Geral | Nova visão | Justificativa |"
    )
    provider = MockProvider(responses={"proponent": mock_response})
    executor = RoundExecutor(provider=provider, board=board, tracker=tracker, builder=builder)
    
    result = executor.execute_defense_round(
        current_proposal=proposal,
        last_critique="Critique",
        round_num=1
    )
    
    assert "Nova visão" in result.updated_proposal
    assert "Original" in result.updated_proposal # Estratégia é APPEND para manter rastro
