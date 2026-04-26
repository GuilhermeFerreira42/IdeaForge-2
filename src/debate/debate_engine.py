import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from src.models.model_provider import ModelProvider
from src.core.validation_board import ValidationBoard
from src.debate.debate_state_tracker import DebateStateTracker
from src.debate.context_builder import ContextBuilder
from src.debate.round_executor import RoundExecutor
from src.core.adaptive_orchestrator import AdaptiveOrchestrator
from src.core.convergence_detector import ConvergenceDetector
from src.agents.specialist_profiles import build_specialist_prompt, get_profile
from src.agents.specialist_factory import SpecialistFactory
from src.core.dynamic_prompt_builder import DynamicPromptBuilder
from src.config.settings import MAX_ROUNDS, MIN_ROUNDS

logger = logging.getLogger(__name__)

@dataclass
class DebateResult:
    """Resultado final do debate consolidado."""
    final_proposal: str
    transcript: List[Dict[str, str]]
    board_snapshot: Dict[str, Any]
    stats: Dict[str, Any]

class DebateEngine:
    """
    Motor do debate IdeaForge 2 (Onda 2).
    Coordena o fluxo adaptativo entre Proponente, Crítico e Especialistas.
    """

    def __init__(self, provider: ModelProvider, board: ValidationBoard, 
                 tracker: DebateStateTracker, builder: ContextBuilder,
                 max_rounds: int = MAX_ROUNDS, min_rounds: int = MIN_ROUNDS):
        self.provider = provider
        self.board = board
        self.tracker = tracker
        self.builder = builder
        self.max_rounds = max_rounds
        self.min_rounds = min_rounds
        
        self.executor = RoundExecutor(provider, board, tracker, builder)
        self.detector = ConvergenceDetector()
        self.orchestrator = AdaptiveOrchestrator(
            board=board, 
            detector=self.detector,
            max_rounds=max_rounds,
            min_rounds=min_rounds
        )
        
        # [ONDA 4] Inicialização Dinâmica
        self.profile = board.get_domain_profile()
        self.prompt_builder = DynamicPromptBuilder(board, self.profile)
        self.specialist_factory = SpecialistFactory(self.profile, self.prompt_builder, provider)
        
        self.transcript = []

    def _log_round(self, role: str, text: str):
        self.transcript.append({"role": role, "content": text})

    def run_debate(self, idea_or_proposal: str) -> DebateResult:
        """
        Executa o debate completo. 
        Se idea_or_proposal não for uma proposta estruturada, executa Round 0 (Expansão).
        """
        current_proposal = idea_or_proposal
        
        # Round 0: Expansão (se necessário)
        if not idea_or_proposal.startswith("# 1."):
            logger.info("[DebateEngine] Iniciando Round 0: Expansão")
            # [ONDA 4] Usando PromptBuilder Dinâmico
            expansion_prompt = self.prompt_builder.build_expansion_prompt(idea_or_proposal)
            current_proposal = self.provider.generate(prompt=expansion_prompt, role="proponent")
            self._log_round("proponent_expansion", current_proposal)
            
        current_round = 1
        last_defense = ""
        last_critique = ""
        stop_reason = ""
        
        while current_round <= self.max_rounds:
            logger.info(f"[DebateEngine] Round {current_round}")
            
            # 1. Turno de Crítica (Base)
            critic_result = self.executor.execute_critic_round(
                current_proposal=current_proposal,
                last_defense=last_defense,
                round_num=current_round
            )
            self._log_round(f"critic_r{current_round}", critic_result.raw_text)
            last_critique = critic_result.raw_text
            
            # 2. Avaliação do Orquestrador
            decision = self.orchestrator.evaluate(
                round_num=current_round,
                current_round_text=critic_result.raw_text,
                previous_round_text=self.transcript[-3]["content"] if len(self.transcript) > 2 else "",
                new_issue_count=critic_result.new_issue_count
            )
            
            if decision.action == "STOP":
                stop_reason = decision.reason
                break
                
            if decision.action == "SPAWN":
                # Turno de Especialista [ONDA 4: DINÂMICO]
                logger.info(f"[DebateEngine] Spawning especialist: {decision.category}")
                specialist = self.specialist_factory.create_specialist(decision.category)
                spec_text = specialist.act(
                    idea=idea_or_proposal,
                    current_proposal=current_proposal,
                    open_issues=self.board.get_open_issues_for_critic_prompt()
                )
                self._log_round(f"specialist_{decision.category}_r{current_round}", spec_text)
                
                # Extrair issues do especialista
                self.tracker.extract_issues_from_critique(
                    self.executor._canonicalize_table(spec_text),
                    current_round,
                    self.board
                )
                
                # [ONDA 4] Registrar o spawn no orquestrador
                self.orchestrator.register_spawn(decision.category)
            
            # 3. Turno de Defesa
            defense_result = self.executor.execute_defense_round(
                current_proposal=current_proposal,
                last_critique=last_critique,
                round_num=current_round
            )
            self._log_round(f"proponent_defense_r{current_round}", defense_result.raw_text)
            last_defense = defense_result.raw_text
            current_proposal = defense_result.updated_proposal
            
            current_round += 1
            
        if not stop_reason:
            stop_reason = f"MAX_ROUNDS ({self.max_rounds}) atingido sem convergência nominal."

        return DebateResult(
            final_proposal=current_proposal,
            transcript=self.transcript,
            board_snapshot=self.board.snapshot(),
            stats={
                "total_rounds": current_round if current_round <= self.max_rounds else self.max_rounds,
                "stop_reason": stop_reason,
                "issues_raised": len(self.board._issues),
                "issues_resolved": len([i for i in self.board._issues.values() if i.status == "RESOLVED"]),
                "parsing_succeeded_count": sum(1 for r in self.transcript if r.get("parsing_succeeded", True)) # Simplificado
            }
        )
