"""
Testes TDD para AdaptiveOrchestrator (W1-05).
Critérios do backlog:
  - issues HIGH → CONTINUE
  - convergência → STOP
  - ≥3 mesma categoria → SPAWN
  - MAX_AGENTS → bloqueio de spawn
  - MAX_ROUNDS → STOP forçado
  - MIN_ROUNDS → nunca STOP antes
"""
import pytest


@pytest.fixture
def board():
    from src.core.validation_board import ValidationBoard
    return ValidationBoard()


@pytest.fixture
def detector():
    from src.core.convergence_detector import ConvergenceDetector
    return ConvergenceDetector()


@pytest.fixture
def orchestrator(board, detector):
    from src.core.adaptive_orchestrator import AdaptiveOrchestrator
    return AdaptiveOrchestrator(board=board, detector=detector)


class TestDecisionContinue:
    """Orquestrador deve retornar CONTINUE quando há issues HIGH abertos."""

    def test_continue_when_high_issues_open(self, orchestrator, board):
        from src.core.validation_board import IssueRecord
        board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Vuln grave"))
        decision = orchestrator.evaluate(
            round_num=3,
            current_round_text="texto do round",
            previous_round_text="texto anterior",
            new_issue_count=1
        )
        assert decision.action == "CONTINUE"

    def test_continue_when_med_issues_only(self, orchestrator, board):
        from src.core.validation_board import IssueRecord
        board.add_issue(IssueRecord("ISS-01", "MED", "CORRECTNESS", "Erro moderado"))
        decision = orchestrator.evaluate(
            round_num=3,
            current_round_text="análise do problema",
            previous_round_text="texto anterior diferente",
            new_issue_count=1
        )
        # MED issues alone → still CONTINUE if not converged
        assert decision.action == "CONTINUE"


class TestDecisionStop:
    """Orquestrador deve retornar STOP em condições apropriadas."""

    def test_stop_at_max_rounds(self, orchestrator, board):
        from src.core.validation_board import IssueRecord
        # Even with HIGH issues, MAX_ROUNDS forces stop
        board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Vuln"))
        decision = orchestrator.evaluate(
            round_num=10,
            current_round_text="round final",
            previous_round_text="round anterior",
            new_issue_count=1
        )
        assert decision.action == "STOP"
        assert "MAX_ROUNDS" in decision.reason

    def test_stop_when_text_70_percent_repeated(self, orchestrator):
        # No issues at all, text is 70%+ repeated
        text_a = "autenticação segurança vulnerabilidade endpoint proteção sistema banco"
        text_b = "autenticação segurança vulnerabilidade endpoint proteção sistema cache"
        # Setup stale rounds for issue stagnation too
        orchestrator.detector.record_round(1, 1)
        orchestrator.detector.record_round(2, 0)
        decision = orchestrator.evaluate(
            round_num=3,
            current_round_text=text_b,
            previous_round_text=text_a,
            new_issue_count=0
        )
        assert decision.action == "STOP"
        assert "convergência" in decision.reason.lower() or "convergence" in decision.reason.lower()

    def test_stop_when_no_open_issues_and_converged(self, orchestrator):
        orchestrator.detector.record_round(1, 2)
        orchestrator.detector.record_round(2, 0)
        decision = orchestrator.evaluate(
            round_num=3,
            current_round_text="repetição do mesmo argumento",
            previous_round_text="repetição do argumento anterior",
            new_issue_count=0
        )
        assert decision.action == "STOP"

    def test_never_stop_before_min_rounds(self, orchestrator):
        """Mesmo sem issues e com convergência, não parar antes de MIN_ROUNDS."""
        decision = orchestrator.evaluate(
            round_num=1,
            current_round_text="texto repetido",
            previous_round_text="texto repetido",
            new_issue_count=0
        )
        assert decision.action == "CONTINUE"


class TestDecisionSpawn:
    """Orquestrador deve retornar SPAWN quando ≥3 issues na mesma categoria."""

    def test_spawn_when_3_same_category(self, orchestrator, board):
        from src.core.validation_board import IssueRecord
        board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Vuln 1"))
        board.add_issue(IssueRecord("ISS-02", "MED", "SECURITY", "Vuln 2"))
        board.add_issue(IssueRecord("ISS-03", "LOW", "SECURITY", "Vuln 3"))
        decision = orchestrator.evaluate(
            round_num=3,
            current_round_text="novos problemas de segurança",
            previous_round_text="texto anterior diferente",
            new_issue_count=1
        )
        assert decision.action == "SPAWN"
        assert decision.category == "SECURITY"

    def test_no_spawn_with_2_same_category(self, orchestrator, board):
        from src.core.validation_board import IssueRecord
        board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Vuln 1"))
        board.add_issue(IssueRecord("ISS-02", "MED", "SECURITY", "Vuln 2"))
        decision = orchestrator.evaluate(
            round_num=3,
            current_round_text="problemas encontrados",
            previous_round_text="texto anterior diferente",
            new_issue_count=1
        )
        assert decision.action != "SPAWN"

    def test_spawn_blocked_at_max_agents(self, board, detector):
        from src.core.adaptive_orchestrator import AdaptiveOrchestrator
        from src.core.validation_board import IssueRecord

        orchestrator = AdaptiveOrchestrator(
            board=board, detector=detector, current_agent_count=5
        )
        board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Vuln 1"))
        board.add_issue(IssueRecord("ISS-02", "MED", "SECURITY", "Vuln 2"))
        board.add_issue(IssueRecord("ISS-03", "LOW", "SECURITY", "Vuln 3"))
        decision = orchestrator.evaluate(
            round_num=3,
            current_round_text="novos problemas",
            previous_round_text="texto anterior diferente",
            new_issue_count=1
        )
        # Should CONTINUE instead of SPAWN because MAX_AGENTS reached
        assert decision.action == "CONTINUE"
        assert "MAX_AGENTS" in decision.reason

    def test_spawn_resolved_issues_not_counted(self, orchestrator, board):
        from src.core.validation_board import IssueRecord
        board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "V1"))
        board.add_issue(IssueRecord("ISS-02", "MED", "SECURITY", "V2", status="RESOLVED"))
        board.add_issue(IssueRecord("ISS-03", "LOW", "SECURITY", "V3", status="DEFERRED"))
        # Only 1 OPEN SECURITY issue → no spawn
        decision = orchestrator.evaluate(
            round_num=3,
            current_round_text="análise de segurança",
            previous_round_text="texto anterior diferente",
            new_issue_count=0
        )
        assert decision.action != "SPAWN"


class TestDecisionDataclass:
    """Testa a estrutura do objeto Decision retornado."""

    def test_decision_has_required_fields(self, orchestrator):
        decision = orchestrator.evaluate(
            round_num=3,
            current_round_text="texto qualquer",
            previous_round_text="texto anterior",
            new_issue_count=0
        )
        assert hasattr(decision, "action")
        assert hasattr(decision, "reason")
        assert hasattr(decision, "category")
        assert decision.action in ("CONTINUE", "STOP", "SPAWN")


class TestEdgeCases:
    """Testes de borda e fallback."""

    def test_stop_exactly_at_round_10(self, orchestrator):
        decision = orchestrator.evaluate(
            round_num=10,
            current_round_text="round 10",
            previous_round_text="round 9",
            new_issue_count=5
        )
        assert decision.action == "STOP"

    def test_continue_at_round_9_with_issues(self, orchestrator, board):
        from src.core.validation_board import IssueRecord
        board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Vuln"))
        decision = orchestrator.evaluate(
            round_num=9,
            current_round_text="round 9 com problemas",
            previous_round_text="round 8 diferente",
            new_issue_count=1
        )
        assert decision.action in ("CONTINUE", "SPAWN")

    def test_spawn_takes_priority_over_continue(self, orchestrator, board):
        """Se há ≥3 issues na mesma categoria E issues HIGH, SPAWN > CONTINUE."""
        from src.core.validation_board import IssueRecord
        board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "V1"))
        board.add_issue(IssueRecord("ISS-02", "HIGH", "SECURITY", "V2"))
        board.add_issue(IssueRecord("ISS-03", "MED", "SECURITY", "V3"))
        decision = orchestrator.evaluate(
            round_num=3,
            current_round_text="muitos problemas de segurança",
            previous_round_text="texto anterior diferente",
            new_issue_count=2
        )
        assert decision.action == "SPAWN"
        assert decision.category == "SECURITY"


class TestZeroLLM:
    """Garantir que o módulo não importa nenhum provider LLM."""

    def test_no_llm_imports_in_orchestrator(self):
        import ast
        with open("src/core/adaptive_orchestrator.py", "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "model_provider" not in alias.name
                    assert "ollama" not in alias.name
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "model_provider" not in node.module
                    assert "ollama" not in node.module
