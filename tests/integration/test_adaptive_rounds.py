"""
Teste de integração: fluxo completo Board + Detector + Orchestrator.
Simula um debate de múltiplos rounds sem LLM.
"""
import pytest
from src.core.validation_board import ValidationBoard, IssueRecord
from src.core.convergence_detector import ConvergenceDetector
from src.core.adaptive_orchestrator import AdaptiveOrchestrator


class TestAdaptiveRoundsIntegration:
    """Simula cenários reais de debate com múltiplos rounds."""

    def test_full_debate_converges_naturally(self):
        board = ValidationBoard()
        detector = ConvergenceDetector()
        orch = AdaptiveOrchestrator(board=board, detector=detector)

        # Round 1: Critic levanta 3 issues
        board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Vuln XSS"))
        board.add_issue(IssueRecord("ISS-02", "MED", "COMPLETENESS", "Falta docs"))
        board.add_issue(IssueRecord("ISS-03", "LOW", "CONSISTENCY", "Typo"))

        d1 = orch.evaluate(1, "xss segurança docs falta", "", 3)
        assert d1.action == "CONTINUE"  # MIN_ROUNDS

        # Round 2: Proponent resolve ISS-01, Critic repete
        board.resolve_issue("ISS-01", 2, "Corrigido XSS")

        d2 = orch.evaluate(
            2, "segurança corrigida docs atualizados",
            "xss segurança docs falta", 0
        )
        # Round 2 = MIN_ROUNDS, pode avaliar convergência
        # Mas text isn't saturated enough and only 1 stale round
        assert d2.action == "CONTINUE"

        # Round 3: Nada novo, texto repetitivo
        board.resolve_issue("ISS-02", 3, "Docs adicionados")

        d3 = orch.evaluate(
            3, "segurança corrigida docs atualizados typo",
            "segurança corrigida docs atualizados", 0
        )
        # 2 stale rounds (rounds 2 and 3 with 0 new issues) → convergence
        assert d3.action == "STOP"

    def test_debate_stops_at_max_rounds(self):
        board = ValidationBoard()
        detector = ConvergenceDetector()
        orch = AdaptiveOrchestrator(board=board, detector=detector, max_rounds=5)

        board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Problema"))

        for r in range(1, 5):
            d = orch.evaluate(r, f"texto {r}", f"texto {r-1}", 1)
            assert d.action in ("CONTINUE", "SPAWN")

        d_final = orch.evaluate(5, "texto 5", "texto 4", 1)
        assert d_final.action == "STOP"

    def test_spawn_then_continue(self):
        board = ValidationBoard()
        detector = ConvergenceDetector()
        orch = AdaptiveOrchestrator(board=board, detector=detector)

        # 3 SECURITY issues → SPAWN
        board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "V1"))
        board.add_issue(IssueRecord("ISS-02", "HIGH", "SECURITY", "V2"))
        board.add_issue(IssueRecord("ISS-03", "MED", "SECURITY", "V3"))

        d = orch.evaluate(3, "segurança problemas", "outro texto", 1)
        assert d.action == "SPAWN"
        assert d.category == "SECURITY"

        # After spawning, simulate agent added
        orch._current_agent_count += 1

        # Resolve some, now CONTINUE
        board.resolve_issue("ISS-01", 4, "Fixed")
        board.resolve_issue("ISS-02", 4, "Fixed")

        d2 = orch.evaluate(4, "segurança melhorada", "segurança problemas", 0)
        assert d2.action in ("CONTINUE", "STOP")
