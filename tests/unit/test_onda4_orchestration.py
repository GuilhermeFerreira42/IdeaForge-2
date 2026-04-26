import pytest
from unittest.mock import MagicMock
from src.core.adaptive_orchestrator import AdaptiveOrchestrator, OrchestratorDecision
from src.core.validation_board import ValidationBoard, IssueRecord
from src.core.convergence_detector import ConvergenceDetector
from src.debate.debate_engine import DebateEngine
from src.core.domain_profile import DomainProfile, ExpansionSection
from src.core.dynamic_prompt_builder import DynamicPromptBuilder

def test_orchestrator_deduplication():
    board = ValidationBoard()
    # Adicionar issues suficientes para spawn em "SECURITY"
    for i in range(5):
        board.add_issue(IssueRecord(f"I{i}", "HIGH", "SECURITY", "Desc"))
    
    detector = MagicMock(spec=ConvergenceDetector)
    detector.is_converged.return_value = False
    orchestrator = AdaptiveOrchestrator(board, detector, spawn_threshold=3)
    
    # Primeiro Spawn deve ser permitido
    decision = orchestrator.evaluate(2, "text", "prev", 5)
    assert decision.action == "SPAWN"
    assert decision.category == "SECURITY"
    
    # Registrar o spawn
    orchestrator.register_spawn("SECURITY")
    
    # Segundo Spawn para a mesma categoria deve ser bloqueado (Deduplicação)
    decision = orchestrator.evaluate(3, "text2", "text", 0)
    assert decision.action == "CONTINUE"
    assert "já foi spawnada" in decision.reason or "deduplicado" in decision.reason.lower() or decision.action != "SPAWN"

def test_engine_initializes_with_profile():
    profile = DomainProfile("software", 1.0, "manual", [], [], [])
    board = ValidationBoard(profile=profile)
    provider = MagicMock()
    
    engine = DebateEngine(provider, board, MagicMock(), MagicMock())
    
    assert engine.prompt_builder is not None
    assert engine.specialist_factory is not None
    assert engine.prompt_builder.profile == profile

def test_engine_uses_dynamic_expansion_round_0():
    profile = DomainProfile(
        domain="physics", 
        confidence=1.0, 
        source="manual", 
        expansion_sections=[ExpansionSection("H1", "Hypothesis", "Explain")],
        validation_dimensions=[],
        report_sections=[]
    )
    board = ValidationBoard(profile=profile)
    provider = MagicMock()
    # Mocking the generator to see if it receives the dynamic prompt
    provider.generate.return_value = "# 1. Hypothesis\nContent"
    
    engine = DebateEngine(provider, board, MagicMock(), MagicMock())
    
    # Executar o debate (Round 0)
    engine.run_debate("Uma ideia de física")
    
    # O prompt enviado ao provider deve conter "Hypothesis" (do profile dinâmico)
    # Verificamos todas as chamadas pois o debate continua após o Round 0
    all_prompts = []
    for call in provider.generate.call_args_list:
        args, kwargs = call
        p = kwargs.get("prompt", "")
        if not p and len(args) > 0:
            p = args[0]
        all_prompts.append(p)
        
    assert any("Hypothesis" in p for p in all_prompts)
