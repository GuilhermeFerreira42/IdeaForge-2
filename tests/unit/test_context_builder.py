import pytest
from src.debate.context_builder import ContextBuilder
from src.core.validation_board import ValidationBoard, IssueRecord

def test_context_builder_assembles_full_prompt():
    """Verifica se o ContextBuilder monta o prompt com todos os componentes."""
    board = ValidationBoard()
    board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Desc"))
    
    builder = ContextBuilder(board=board)
    prompt = builder.build_defense_prompt(
        current_proposal="Proposta V1",
        last_critique="Crítica do round",
        last_defense="Defesa anterior"
    )
    
    assert "Proposta V1" in prompt
    assert "ISS-01" in prompt
    assert "Crítica do round" in prompt
    assert "Agente Proponente" in prompt

def test_under_3000_chars_invariable():
    """Garante que o prompt montado nunca excede 3000 caracteres."""
    board = ValidationBoard()
    # Adicionar muitos issues para tentar estourar o budget
    for i in range(50):
        board.add_issue(IssueRecord(f"ISS-{i}", "HIGH", "SECURITY", "Desc" * 20))
    
    builder = ContextBuilder(board=board)
    prompt = builder.build_defense_prompt(
        current_proposal="P" * 2000,
        last_critique="C" * 2000,
        last_defense="D" * 2000
    )
    
    assert len(prompt) <= 3000

def test_priority_truncation_rule_order():
    """Verifica se a prioridade de truncamento é respeitada [COR-13].
    Ordem de prioridade (preservar mais): 
    1. System > 2. Issues > 3. Defesa > 4. Proposta > 5. Decisões (decisões são menos prioritárias se grandes)
    Na verdade, o blueprint diz:
    1. System (600)
    2. Issues (600)
    3. Last Response (700)
    4. Current Proposal (800)
    5. Validated Decisions (300)
    """
    board = ValidationBoard()
    builder = ContextBuilder(board=board)
    
    # Simular budgets estourados
    prompt = builder.build_defense_prompt(
        current_proposal="P" * 2000,
        last_critique="C" * 1500,
        last_defense="D" * 1500
    )
    
    # O prompt final deve ter partes de tudo, mas truncado
    assert "P" * 797 + "..." in prompt # Proposal budget
    assert "C" * 697 + "..." in prompt # Response budget (critique)
    assert len(prompt) <= 3000
