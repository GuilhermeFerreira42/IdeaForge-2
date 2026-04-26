import logging
import sys
import json
from datetime import datetime
from typing import Dict, Any, Optional

from src.debate.debate_engine import DebateEngine
from src.debate.debate_state_tracker import DebateStateTracker
from src.debate.context_builder import ContextBuilder
from src.core.validation_board import ValidationBoard
from src.core.domain_detector import DomainDetector
from src.core.domain_context_builder import DomainContextBuilder
from src.agents.synthesizer_agent import SynthesizerAgent
from src.core.report_generator import ReportGenerator
from src.models.ollama_provider import OllamaProvider, OllamaMemoryError, OllamaServiceError
from src.models.cloud_provider import CloudProvider
from src.config import settings

logger = logging.getLogger(__name__)

class Controller:
    """
    Entry point do pipeline IdeaForge 2 (Onda 3).
    Coordena: Expansão -> Debate -> Síntese -> Persistência.
    """

    def __init__(self):
        self.tracker = DebateStateTracker()
        self.synthesizer = SynthesizerAgent()
        self.generator = ReportGenerator()

    def run(self, idea: str, model_name: str, think: bool = False, debug: bool = False) -> Dict[str, Any]:
        """
        Executa o fluxo completo do sistema.
        """
        if not idea.strip():
            return {"status": "error", "error": "Ideia não pode ser vazia"}

        # 1. Setup providers
        try:
            # A seleção de provedor via sufixo "-cloud" estava forçando uso de Mock.
            # Como a lista de modelos vem do Ollama, forçamos o uso do OllamaProvider.
            is_cloud = False
            provider = self._get_provider(model_name, think, is_cloud)
            
            # === ROUND 0A: Meta-Orquestração ===
            logger.info(f"[Controller] Round 0A: Detectando domínio para '{idea[:50]}...'")
            detector = DomainDetector()
            domain_result = detector.detect(idea)
            logger.info(f"[Controller] Domínio detectado: {domain_result.domain} (Conf: {domain_result.confidence})")
            
            context_builder = DomainContextBuilder(provider)
            profile = context_builder.build(idea, domain_result.domain)
            logger.info(f"[Controller] DomainProfile construído via {profile.source}")
            
            # Inicializa Board com o Profile
            board = ValidationBoard(profile=profile)
            builder = ContextBuilder(board)
            engine = DebateEngine(provider, board, self.tracker, builder)
        except OllamaMemoryError as e:
            return {"status": "memory_error", "error": f"Memória insuficiente no Ollama: {e}"}
        except OllamaServiceError as e:
            return {"status": "error", "error": f"Erro no serviço Ollama: {e}"}
        except Exception as e:
            return {"status": "error", "error": f"Erro de inicialização: {e}"}

        # 2. Executa Debate
        logger.info(f"Iniciando debate para a ideia: '{idea}'")
        try:
            debate_result = engine.run_debate(idea)
        except OllamaMemoryError as e:
            return {"status": "memory_error", "error": f"Memória insuficiente durante o debate: {e}"}
        except Exception as e:
            logger.error(f"Falha catastrófica no motor de debate: {e}")
            return {"status": "error", "error": f"Debate Engine failure: {e}"}

        if debug:
            self._emit_debug(debate_result)

        # 3. Gera Relatório
        output_path = self._get_output_path(idea)
        logger.info(f"Sintetizando relatório final...")
        report_result = self.generator.generate(
            board=board,
            synthesizer=self.synthesizer,
            idea_title=idea,
            output_path=output_path,
            provider=provider
        )

        if report_result["status"] == "error":
            return report_result

        # 4. Consolidar Resultado
        return {
            "status": "success",
            "output_path": report_result["output_path"],
            "debate_rounds": debate_result.stats.get("total_rounds", 0),
            "issues_total": debate_result.stats.get("issues_raised", 0),
            "fallback_used": report_result["fallback_used"],
            "model_used": model_name
        }

    def _get_provider(self, model_name: str, think: bool, is_cloud: bool = False) -> Any:
        """Instancia o provedor de modelo (Ollama ou Cloud)."""
        if is_cloud:
            # CloudProvider assumido como existente para gpt-oss:20b-cloud
            return CloudProvider(model_name=model_name)
        return OllamaProvider(model_name=model_name, think=think, show_thinking=think)

    def _get_output_path(self, idea_title: str) -> str:
        """Gera o nome do arquivo com timestamp conforme ADR-W3-05."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"debate_RELATORIO_{timestamp}.md"

    def _emit_debug(self, result: Any) -> None:
        """Emite dados de debug para o stderr."""
        sys.stderr.write("\n" + "="*40 + "\n")
        sys.stderr.write("DEBUG INFO (IdeaForge 2)\n")
        sys.stderr.write("="*40 + "\n")
        sys.stderr.write(f"Stop Reason: {result.stats.get('stop_reason', 'Unknown')}\n")
        sys.stderr.write("-" * 20 + "\n")
        sys.stderr.write("BOARD SNAPSHOT:\n")
        sys.stderr.write(json.dumps(result.board_snapshot, indent=2, ensure_ascii=False) + "\n")
        sys.stderr.write("-" * 20 + "\n")
        sys.stderr.write("TRANSCRIPT:\n")
        for entry in result.transcript:
            sys.stderr.write(f"[{entry['role']}]: {entry['content'][:200]}...\n")
        sys.stderr.write("="*40 + "\n\n")
