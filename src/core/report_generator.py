import logging
import os
import json
from typing import Dict, Any

from src.core.validation_board import ValidationBoard
from src.agents.synthesizer_agent import SynthesizerAgent

logger = logging.getLogger(__name__)

class ReportGenerator:
    """
    Gerencia a persistência do relatório final e o fallback determinístico.
    Responsabilidade: W3-02.
    """

    def generate(self, board: ValidationBoard, synthesizer: SynthesizerAgent, 
                 idea_title: str, output_path: str, provider: Any) -> Dict[str, Any]:
        """
        Tenta gerar o relatório via Synthesizer. Se falhar, usa fallback.
        """
        fallback_used = False
        source = "synthesizer"
        
        synth_result = synthesizer.synthesize(board, idea_title, provider)
        
        # Lógica de Fallback (ADR-W3-02 + COR-15)
        # Falha se status="error" OU se tiver < 3 seções obrigatórias
        if synth_result["status"] == "error" or len(synth_result.get("sections_present", [])) < 3:
            logger.warning(f"SynthesizerAgent falhou ou gerou relatório incompleto. Acionando fallback.")
            report_markdown = self._fallback_dump(board, idea_title)
            fallback_used = True
            source = "fallback"
            sections_present = []
        else:
            report_markdown = synth_result["report_markdown"]
            sections_present = synth_result["sections_present"]

        try:
            self._persist(report_markdown, output_path)
            return {
                "status": "success",
                "source": source,
                "output_path": output_path,
                "fallback_used": fallback_used,
                "sections_present": sections_present,
                "board_stats": board.get_stats()
            }
        except Exception as e:
            logger.error(f"Falha crítica na persistência do arquivo: {e}")
            return {
                "status": "error",
                "error": str(e),
                "output_path": output_path
            }

    def _fallback_dump(self, board: ValidationBoard, idea_title: str) -> str:
        """
        Gera um dump legível do board sem depender de LLM.
        """
        snapshot = board.snapshot()
        stats = board.get_stats()
        
        lines = [
            f"# Relatório de Validação — IdeaForge (Fallback Automático)",
            f"> Gerado por fallback determinístico. O SynthesizerAgent falhou.",
            f"",
            f"**Ideia Analisada:** {idea_title}",
            f"",
            f"## Estatísticas do Debate",
            f"- Issues Totais: {stats['total_issues']}",
            f"- Issues Abertos: {stats['open_issues']}",
            f"- Decisões Validadas: {stats['validated_decisions']} / {stats['total_decisions']}",
            f"- Pressupostos: {stats['total_assumptions']} ({stats['untested_assumptions']} pendentes)",
            f"",
            f"## Issues Encontrados",
        ]
        
        for issue_id, issue in snapshot["issues"].items():
            lines.append(f"- **{issue_id}** [{issue['severity']}] ({issue['category']}): {issue['description']}")
            lines.append(f"  - Status: {issue['status']}")
            
        lines.append(f"")
        lines.append(f"## Decisões Tomadas")
        for dec_id, dec in snapshot["decisions"].items():
            lines.append(f"- **{dec_id}**: {dec['description']} (Status: {dec['status']})")
            
        lines.append(f"")
        lines.append(f"## Pressupostos Mapeados")
        for ass_id, ass in snapshot["assumptions"].items():
            lines.append(f"- **{ass_id}**: {ass['description']} (Status: {ass['status']})")
            
        return "\n".join(lines)

    def _persist(self, content: str, output_path: str) -> None:
        """
        Salva o conteúdo em disco.
        """
        # Garante que o diretório pai existe
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Relatório persistido em: {output_path}")
