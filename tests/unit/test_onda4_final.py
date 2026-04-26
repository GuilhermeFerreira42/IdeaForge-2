import pytest
from unittest.mock import MagicMock
from src.core.validation_board import ValidationBoard
from src.core.domain_profile import DomainProfile, ValidationDimension, ReportSection
from src.debate.debate_state_tracker import DebateStateTracker
from src.agents.synthesizer_agent import SynthesizerAgent
from src.core.report_generator import ReportGenerator

def test_parser_v4_supports_4_column_table():
    tracker = DebateStateTracker()
    board = ValidationBoard()
    table = "| Severidade | Categoria | Descrição | Sugestão |\n| HIGH | SECURITY | Falha X | Mitigar |"
    
    ids = tracker.extract_issues_from_critique(table, 1, board)
    
    assert len(ids) == 1
    issue = board.get_issue(ids[0])
    assert issue.severity == "HIGH"
    assert issue.category == "SECURITY"
    assert "Falha X" in issue.description

def test_category_normalization_during_extraction():
    # Mocking normalizer behavior or assuming it's integrated
    profile = DomainProfile(
        domain="tech", confidence=1.0, source="manual",
        expansion_sections=[],
        validation_dimensions=[
            ValidationDimension("SEC", "Segurança", "D", "H")
        ],
        report_sections=[]
    )
    board = ValidationBoard(profile=profile)
    tracker = DebateStateTracker() # Deve usar normalizer internamente na Onda 4
    
    # LLM gerou "segurança cibernética" que deve ser normalizada para "SEC"
    table = "| HIGH | segurança cibernética | Risco Hacker | Firewall |"
    ids = tracker.extract_issues_from_critique(table, 1, board)
    
    issue = board.get_issue(ids[0])
    assert issue.category == "SEC"

def test_synthesizer_uses_dynamic_sections():
    profile = DomainProfile(
        domain="space", confidence=1.0, source="manual",
        expansion_sections=[],
        validation_dimensions=[],
        report_sections=[
            ReportSection(id="PROPULSION", title="## Análise de Propulsão", template="Análise técnica")
        ]
    )
    board = ValidationBoard(profile=profile)
    provider = MagicMock()
    agent = SynthesizerAgent()
    
    # Simular sucesso do provider
    provider.generate.return_value = "## Análise de Propulsão\nFoguete top."
    
    result = agent.synthesize(board, "Foguete", provider)
    assert "## Análise de Propulsão" in result["sections_present"]
