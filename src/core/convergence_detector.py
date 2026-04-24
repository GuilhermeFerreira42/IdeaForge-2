"""
convergence_detector.py -- Detector programático de convergência do debate.

W1-04:
Responsabilidade:
  - Medir similaridade textual entre rounds via Jaccard (bag-of-words)
  - Detectar saturação de issues (N rounds sem novos problemas)
  - Fornecer veredito de convergência para o AdaptiveOrchestrator

Contrato:
  - 100% programático -- zero chamadas LLM
  - Usa Jaccard com stopwords PT (threshold configurável, default 0.7)
  - Convergência = saturação textual OU saturação de issues
"""
import logging
from typing import List

from src.config.settings import CONVERGENCE_THRESHOLD, CONVERGENCE_STALE_ROUNDS

logger = logging.getLogger(__name__)

STOPWORDS_PT = {
    "o", "a", "de", "que", "para", "com", "em", "é", "um", "uma",
    "os", "as", "do", "da", "dos", "das", "no", "na", "nos", "nas",
    "se", "ao", "por", "mais", "não", "como", "mas", "ou", "este",
    "essa", "esse", "isso", "ser", "ter", "foi", "são", "está",
    "e", "à", "já", "também", "seu", "sua", "seus", "suas",
    "ele", "ela", "eles", "elas", "nos", "lhe", "lhes",
}


class ConvergenceDetector:
    """
    Detector de convergência 100% programático.

    Duas dimensões independentes:
      1. Saturação textual: Jaccard similarity > threshold entre rounds
      2. Saturação de issues: N rounds consecutivos sem novos issues

    Qualquer uma das duas condições satisfeita → convergência = True.
    """

    def __init__(
        self,
        similarity_threshold: float = CONVERGENCE_THRESHOLD,
        stale_rounds: int = CONVERGENCE_STALE_ROUNDS,
    ):
        self._threshold = similarity_threshold
        self._stale_rounds = stale_rounds
        self._round_history: List[int] = []  # new_issue_count por round

    def similarity(self, text_a: str, text_b: str) -> float:
        """
        Similaridade Jaccard entre dois textos usando bag-of-words.
        Stopwords PT são removidas antes da comparação.

        Returns:
            float entre 0.0 e 1.0. 0.0 se ambos vazios ou apenas stopwords.
        """
        if not text_a.strip() and not text_b.strip():
            return 0.0

        words_a = set(text_a.lower().split()) - STOPWORDS_PT
        words_b = set(text_b.lower().split()) - STOPWORDS_PT

        if not words_a and not words_b:
            return 0.0

        union = words_a | words_b
        if not union:
            return 0.0

        intersection = words_a & words_b
        return len(intersection) / len(union)

    def is_text_saturated(self, current_text: str, previous_text: str) -> bool:
        """True se similarity > threshold."""
        if not current_text or not previous_text:
            return False
        sim = self.similarity(current_text, previous_text)
        logger.debug(f"[ConvergenceDetector] Jaccard similarity: {sim:.3f} (threshold: {self._threshold})")
        return sim >= self._threshold

    def record_round(self, round_num: int, new_issue_count: int) -> None:
        """Registra contagem de novos issues para o round."""
        self._round_history.append(new_issue_count)
        logger.debug(
            f"[ConvergenceDetector] Round {round_num}: "
            f"{new_issue_count} novos issues (histórico: {self._round_history})"
        )

    def is_issue_stagnant(self) -> bool:
        """
        True se os últimos N rounds consecutivos tiveram 0 novos issues.
        N = self._stale_rounds (default 2).
        """
        if len(self._round_history) < self._stale_rounds:
            return False

        last_n = self._round_history[-self._stale_rounds:]
        return all(count == 0 for count in last_n)

    def is_converged(
        self,
        current_round_text: str,
        previous_round_text: str,
        new_issue_count: int,
        round_num: int,
    ) -> bool:
        """
        Método principal de convergência.

        Registra o round atual e avalia:
          1. Saturação textual (Jaccard > threshold)
          2. Saturação de issues (N rounds sem novos)

        Returns:
            True se qualquer condição de convergência for atendida.
        """
        self.record_round(round_num, new_issue_count)

        text_saturated = self.is_text_saturated(current_round_text, previous_round_text)
        issue_stagnant = self.is_issue_stagnant()

        if text_saturated:
            logger.info(
                f"[ConvergenceDetector] Convergência por saturação textual "
                f"(Jaccard >= {self._threshold}) no round {round_num}"
            )

        if issue_stagnant:
            logger.info(
                f"[ConvergenceDetector] Convergência por saturação de issues "
                f"({self._stale_rounds} rounds sem novos issues) no round {round_num}"
            )

        return text_saturated or issue_stagnant
