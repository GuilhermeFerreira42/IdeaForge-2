import pytest
from src.core.validation_board import ValidationBoard, IssueRecord, DecisionRecord, AssumptionRecord
from src.debate.debate_state_tracker import DebateStateTracker
from tests.fixtures.mock_critic_responses import TABLE_RESPONSE, BULLETS_RESPONSE
from tests.fixtures.mock_proponent_responses import RESOLUTIONS_RESPONSE
from tests.fixtures.sample_ideas import ROUND0_RESPONSE

@pytest.fixture
def tracker():
    return DebateStateTracker()

@pytest.fixture
def board():
    return ValidationBoard()

def test_extract_level1_table(tracker, board):
    ids = tracker.extract_issues_from_critique(TABLE_RESPONSE, 1, board)
    assert len(ids) == 3
    assert len(board.get_open_issues()) == 3

def test_extract_level2_bullets(tracker, board):
    ids = tracker.extract_issues_from_critique(BULLETS_RESPONSE, 1, board)
    assert len(ids) >= 1
    assert len(board.get_open_issues()) >= 1

def test_extract_resolutions_marks_resolved(tracker, board):
    # Setup open issues
    board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Test 1"))
    board.add_issue(IssueRecord("ISS-02", "MED", "CORRECTNESS", "Test 2"))
    
    resolved_ids = tracker.extract_resolutions_from_defense(RESOLUTIONS_RESPONSE, 1, board)
    assert "ISS-01" in resolved_ids
    assert board._issues["ISS-01"].status == "RESOLVED"
    
def test_extract_decisions_from_proponent(tracker, board):
    text = "## Decisões\n- D-01: usar Jaccard\n- D-02: focar em resiliencia"
    ids = tracker.extract_decisions_from_text(text, 1, board)
    assert "D-01" in ids
    assert "D-01" in board._decisions
    
def test_register_assumptions_from_round0(tracker, board):
    tracker.register_assumptions_from_text(ROUND0_RESPONSE, 0, board)
    assumptions = board.get_untested_assumptions()
    assert len(assumptions) >= 1

def test_dedup_normalized_description(tracker, board):
    # Pass two texts that should mean the same issue
    text1 = "| ISS-01 | HIGH | SECURITY | Falha de login no servidor |"
    text2 = "| ISS-02 | HIGH | SECURITY | Fálha de login   no servidor!! |"
    tracker.extract_issues_from_critique(text1, 1, board)
    tracker.extract_issues_from_critique(text2, 2, board)
    
    # Should only have 1 issue in board
    assert len(board._issues) == 1

def test_is_semantic_duplicate_identifica_duplicata(tracker, board):
    """W5Q-03: Frases semânticas similares devem ser detectadas como duplicadas."""
    board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "O banco de dados está exposto sem senha na porta 5432."))
    
    # Frase muito similar
    new_desc = "O banco de dados está exposto sem senha na porta 5432, vulnerabilidade grave."
    assert tracker._is_semantic_duplicate(new_desc, board, "SECURITY") is True

def test_is_semantic_duplicate_ignora_diferentes(tracker, board):
    """W5Q-03: Frases de categorias diferentes ou temas distintos não são duplicadas."""
    board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "O banco de dados está exposto."))
    
    # Mesmo tema, categoria diferente (não deve ser duplicata se categorias forem tratadas isoladas)
    # Ou tema totalmente diferente
    new_desc = "O sistema está lento para processar imagens grandes."
    assert tracker._is_semantic_duplicate(new_desc, board, "PERFORMANCE") is False

def test_is_semantic_duplicate_usa_stopwords(tracker, board):
    """W5Q-03: A comparação deve ignorar stopwords para ser puramente semântica."""
    board.add_issue(IssueRecord("ISS-01", "HIGH", "SEC", "Falha de segurança."))
    # "Uma" e "a" são stopwords, "falha" e "segurança" são o núcleo.
    new_desc = "Uma falha a segurança."
    assert tracker._is_semantic_duplicate(new_desc, board, "SEC") is True
