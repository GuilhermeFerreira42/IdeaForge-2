import pytest
from src.core.validation_board import ValidationBoard
from src.debate.debate_state_tracker import DebateStateTracker

@pytest.fixture
def board():
    return ValidationBoard()

@pytest.fixture
def tracker():
    return DebateStateTracker()

def test_level3_keyword_heuristic(tracker, board):
    text = "Existe uma vulnerabilidade crítica no sistema de autenticação."
    ids = tracker.extract_issues_from_critique(text, 1, board)
    assert len(ids) >= 1
    issue_id = ids[0]
    assert issue_id in board._issues
    assert board._issues[issue_id].severity == "HIGH"
    assert board._issues[issue_id].category == "SECURITY"

def test_parser_returns_empty_on_no_match(tracker, board):
    text = "Tudo parece ótimo, não vejo problemas no texto, a ideia é boa."
    ids = tracker.extract_issues_from_critique(text, 1, board)
    assert ids == []
    assert len(board._issues) == 0

def test_no_llm_imports():
    import ast
    
    def check_imports(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        assert "model_provider" not in alias.name
                elif isinstance(node, ast.ImportFrom):
                    assert node.module is not None
                    assert "model_provider" not in node.module
                    
    check_imports("src/core/validation_board.py")
    check_imports("src/debate/debate_state_tracker.py")
