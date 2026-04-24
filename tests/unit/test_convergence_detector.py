"""
Testes TDD para ConvergenceDetector (W1-04).
Criterios do backlog:
  - textos iguais → similarity 1.0
  - textos completamente diferentes → similarity < 0.3
  - convergência detectada corretamente (2 rounds sem issues novos)
  - threshold 0.7 para saturação textual
"""
import pytest


@pytest.fixture
def detector():
    from src.core.convergence_detector import ConvergenceDetector
    return ConvergenceDetector()


class TestJaccardSimilarity:
    """Testes da similaridade Jaccard bag-of-words com stopwords PT."""

    def test_identical_texts_return_1(self, detector):
        text = "O sistema precisa de autenticação robusta para segurança"
        assert detector.similarity(text, text) == 1.0

    def test_completely_different_texts_return_low(self, detector):
        text_a = "autenticação robusta segurança endpoint vulnerabilidade"
        text_b = "escalabilidade gargalo throughput performance banco dados"
        sim = detector.similarity(text_a, text_b)
        assert sim < 0.3

    def test_partially_similar_texts(self, detector):
        text_a = "autenticação segurança sistema vulnerabilidade"
        text_b = "autenticação segurança sistema proteção firewall"
        sim = detector.similarity(text_a, text_b)
        assert 0.3 < sim < 0.9

    def test_stopwords_are_filtered(self, detector):
        # Textos que diferem apenas em stopwords devem ser idênticos
        text_a = "o sistema de autenticação é muito importante para a segurança"
        text_b = "sistema autenticação muito importante segurança"
        sim = detector.similarity(text_a, text_b)
        assert sim == 1.0

    def test_empty_texts_return_0(self, detector):
        assert detector.similarity("", "") == 0.0

    def test_one_empty_one_not_return_0(self, detector):
        assert detector.similarity("", "algum conteúdo técnico") == 0.0

    def test_only_stopwords_return_0(self, detector):
        text = "o a de que para com em é um uma os as do da"
        assert detector.similarity(text, text) == 0.0


class TestTextSaturation:
    """Testes de saturação textual (Jaccard > threshold)."""

    def test_70_percent_repeated_triggers_saturation(self, detector):
        # Texto com ~70% overlap
        text_a = "autenticação segurança vulnerabilidade endpoint proteção sistema banco"
        text_b = "autenticação segurança vulnerabilidade endpoint proteção sistema cache"
        sim = detector.similarity(text_a, text_b)
        # 6 palavras em comum de 8 total → 6/8 = 0.75
        assert sim >= 0.7
        assert detector.is_text_saturated(text_a, text_b)

    def test_below_threshold_not_saturated(self, detector):
        text_a = "autenticação segurança vulnerabilidade"
        text_b = "escalabilidade performance gargalo throughput banco"
        assert not detector.is_text_saturated(text_a, text_b)

    def test_custom_threshold(self):
        from src.core.convergence_detector import ConvergenceDetector
        detector = ConvergenceDetector(similarity_threshold=0.9)
        text_a = "autenticação segurança sistema"
        text_b = "autenticação segurança sistema proteção"
        # 3/4 = 0.75 → below 0.9
        assert not detector.is_text_saturated(text_a, text_b)


class TestIssueStagnation:
    """Testes de saturação de issues (2 rounds sem novos problemas)."""

    def test_no_new_issues_for_2_rounds_converged(self, detector):
        # Simula rounds com contagens de issues
        detector.record_round(round_num=1, new_issue_count=3)
        assert not detector.is_issue_stagnant()

        detector.record_round(round_num=2, new_issue_count=0)
        assert not detector.is_issue_stagnant()

        detector.record_round(round_num=3, new_issue_count=0)
        assert detector.is_issue_stagnant()

    def test_new_issues_reset_stagnation(self, detector):
        detector.record_round(round_num=1, new_issue_count=2)
        detector.record_round(round_num=2, new_issue_count=0)
        detector.record_round(round_num=3, new_issue_count=1)  # Reset
        detector.record_round(round_num=4, new_issue_count=0)
        assert not detector.is_issue_stagnant()  # Only 1 stale round

    def test_stagnation_with_custom_stale_rounds(self):
        from src.core.convergence_detector import ConvergenceDetector
        detector = ConvergenceDetector(stale_rounds=3)
        detector.record_round(1, 2)
        detector.record_round(2, 0)
        detector.record_round(3, 0)
        assert not detector.is_issue_stagnant()  # Need 3 stale
        detector.record_round(4, 0)
        assert detector.is_issue_stagnant()

    def test_empty_history_not_stagnant(self, detector):
        assert not detector.is_issue_stagnant()


class TestConvergenceDetection:
    """Testes do método principal is_converged()."""

    def test_converged_by_text_saturation(self, detector):
        text_a = "autenticação segurança vulnerabilidade endpoint proteção sistema banco"
        text_b = "autenticação segurança vulnerabilidade endpoint proteção sistema cache"
        # Round history doesn't matter if text is saturated
        assert detector.is_converged(
            current_round_text=text_b,
            previous_round_text=text_a,
            new_issue_count=0,
            round_num=3
        )

    def test_converged_by_issue_stagnation(self, detector):
        detector.record_round(1, 3)
        detector.record_round(2, 0)
        # Round 3 with 0 new issues → 2 consecutive stale rounds
        assert detector.is_converged(
            current_round_text="texto completamente novo diferente",
            previous_round_text="outro texto totalmente distinto anterior",
            new_issue_count=0,
            round_num=3
        )

    def test_not_converged_with_new_issues(self, detector):
        detector.record_round(1, 3)
        # New issues found, different text
        assert not detector.is_converged(
            current_round_text="novo problema encontrado no sistema",
            previous_round_text="texto anterior completamente diferente",
            new_issue_count=2,
            round_num=2
        )

    def test_not_converged_before_min_data(self, detector):
        # First round, nothing to compare
        assert not detector.is_converged(
            current_round_text="primeira análise do sistema",
            previous_round_text="",
            new_issue_count=3,
            round_num=1
        )


class TestZeroLLM:
    """Garantir que o módulo não importa nenhum provider LLM."""

    def test_no_llm_imports_in_convergence_detector(self):
        import ast
        with open("src/core/convergence_detector.py", "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert "model_provider" not in alias.name
                    assert "ollama" not in alias.name
                    assert "cloud_provider" not in alias.name
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    assert "model_provider" not in node.module
                    assert "ollama" not in node.module
                    assert "cloud_provider" not in node.module
