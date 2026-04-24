"""
adaptive_orchestrator.py -- Maestro do debate adaptativo.

W1-05:
Responsabilidade:
  - Decidir CONTINUE / STOP / SPAWN após cada round
  - Respeitar limites rígidos: MAX_ROUNDS, MAX_AGENTS, MIN_ROUNDS
  - Usar dados do ValidationBoard + ConvergenceDetector
  - Único responsável pelo fluxo do debate

Contrato:
  - 100% programático -- zero chamadas LLM
  - Retorna OrchestratorDecision com action, reason, category
  - Prioridade: MAX_ROUNDS(STOP) > MIN_ROUNDS(CONTINUE) > SPAWN > CONVERGENCE(STOP) > CONTINUE
"""
import logging
from collections import Counter
from dataclasses import dataclass
from typing import Optional

from src.config.settings import MAX_ROUNDS, MAX_AGENTS, MIN_ROUNDS, SPAWN_ISSUE_THRESHOLD
from src.core.convergence_detector import ConvergenceDetector
from src.core.validation_board import ValidationBoard

logger = logging.getLogger(__name__)


@dataclass
class OrchestratorDecision:
    """Resultado da avaliação do orquestrador."""
    action: str       # "CONTINUE" | "STOP" | "SPAWN"
    reason: str       # Justificativa legível
    category: Optional[str] = None  # Categoria para SPAWN (ex: "SECURITY")


class AdaptiveOrchestrator:
    """
    Orquestrador adaptativo 100% determinístico.

    Lógica de decisão (em ordem de prioridade):
      1. round_num >= MAX_ROUNDS → STOP (forçado)
      2. round_num < MIN_ROUNDS → CONTINUE (forçado)
      3. ≥ SPAWN_THRESHOLD issues OPEN na mesma categoria → SPAWN (se < MAX_AGENTS)
      4. Convergência detectada (texto OU issues) → STOP
      5. Default → CONTINUE
    """

    def __init__(
        self,
        board: ValidationBoard,
        detector: ConvergenceDetector,
        max_rounds: int = MAX_ROUNDS,
        max_agents: int = MAX_AGENTS,
        min_rounds: int = MIN_ROUNDS,
        spawn_threshold: int = SPAWN_ISSUE_THRESHOLD,
        current_agent_count: int = 2,  # Proponent + Critic como baseline
    ):
        self.board = board
        self.detector = detector
        self._max_rounds = max_rounds
        self._max_agents = max_agents
        self._min_rounds = min_rounds
        self._spawn_threshold = spawn_threshold
        self._current_agent_count = current_agent_count

    def evaluate(
        self,
        round_num: int,
        current_round_text: str,
        previous_round_text: str,
        new_issue_count: int,
    ) -> OrchestratorDecision:
        """
        Avalia o estado do debate e retorna decisão.

        Args:
            round_num: Número do round atual (1-based)
            current_round_text: Texto completo do round atual
            previous_round_text: Texto completo do round anterior
            new_issue_count: Quantidade de novos issues extraídos neste round

        Returns:
            OrchestratorDecision com action, reason e category (se SPAWN)
        """
        logger.info(
            f"[Orchestrator] Avaliando round {round_num}: "
            f"{new_issue_count} novos issues, "
            f"{len(self.board.get_open_issues())} issues abertos"
        )

        # 1. Limite rígido: MAX_ROUNDS → STOP forçado
        if round_num >= self._max_rounds:
            open_count = len(self.board.get_open_issues())
            reason = (
                f"MAX_ROUNDS ({self._max_rounds}) atingido. "
                f"{open_count} issue(s) ainda aberto(s)."
            )
            logger.info(f"[Orchestrator] STOP: {reason}")
            return OrchestratorDecision(action="STOP", reason=reason)

        # 2. Limite rígido: MIN_ROUNDS → CONTINUE forçado
        if round_num < self._min_rounds:
            reason = f"MIN_ROUNDS ({self._min_rounds}) não atingido. Round {round_num}."
            logger.info(f"[Orchestrator] CONTINUE: {reason}")
            return OrchestratorDecision(action="CONTINUE", reason=reason)

        # 3. Verificar necessidade de SPAWN (≥ threshold issues na mesma categoria)
        spawn_decision = self._check_spawn()
        if spawn_decision is not None:
            return spawn_decision

        # 4. Verificar convergência
        converged = self.detector.is_converged(
            current_round_text=current_round_text,
            previous_round_text=previous_round_text,
            new_issue_count=new_issue_count,
            round_num=round_num,
        )

        if converged:
            open_issues = self.board.get_open_issues()
            has_high = any(i.severity == "HIGH" for i in open_issues)

            if has_high:
                # Convergência detectada mas há issues HIGH → avisar mas parar
                reason = (
                    f"Convergência detectada no round {round_num}, "
                    f"mas {len(open_issues)} issue(s) HIGH ainda aberto(s). "
                    f"Debate encerrado por convergência."
                )
            else:
                reason = (
                    f"Convergência detectada no round {round_num}. "
                    f"Debate esgotou argumentos novos."
                )

            logger.info(f"[Orchestrator] STOP: {reason}")
            return OrchestratorDecision(action="STOP", reason=reason)

        # 5. Default: CONTINUE
        open_count = len(self.board.get_open_issues())
        reason = f"Debate em andamento. {open_count} issue(s) aberto(s). Round {round_num}."
        logger.info(f"[Orchestrator] CONTINUE: {reason}")
        return OrchestratorDecision(action="CONTINUE", reason=reason)

    def _check_spawn(self) -> Optional[OrchestratorDecision]:
        """
        Verifica se alguma categoria tem ≥ spawn_threshold issues OPEN.

        Returns:
            OrchestratorDecision(SPAWN) ou None.
        """
        open_issues = self.board.get_open_issues()
        if not open_issues:
            return None

        # Contar issues OPEN por categoria
        category_counts: Counter = Counter()
        for issue in open_issues:
            category_counts[issue.category] += 1

        # Encontrar categoria dominante
        dominant_category, count = category_counts.most_common(1)[0]

        if count < self._spawn_threshold:
            return None

        # Verificar limite de agentes
        if self._current_agent_count >= self._max_agents:
            reason = (
                f"MAX_AGENTS ({self._max_agents}) atingido. "
                f"Spawn de especialista {dominant_category} bloqueado. "
                f"{count} issues na categoria."
            )
            logger.warning(f"[Orchestrator] CONTINUE (spawn bloqueado): {reason}")
            return OrchestratorDecision(action="CONTINUE", reason=reason)

        reason = (
            f"{count} issues OPEN na categoria {dominant_category} "
            f"(threshold: {self._spawn_threshold}). "
            f"Spawning agente especializado."
        )
        logger.info(f"[Orchestrator] SPAWN: {reason}")
        return OrchestratorDecision(
            action="SPAWN",
            reason=reason,
            category=dominant_category,
        )
