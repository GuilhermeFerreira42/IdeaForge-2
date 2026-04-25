import json
import logging
from typing import Dict, Any, List

from src.models.model_provider import ModelProvider
from src.core.validation_board import ValidationBoard

logger = logging.getLogger(__name__)

class SynthesizerAgent:
    """
    Juíza neutra que converte o estado do ValidationBoard em um relatório Markdown.
    Responsabilidade: W3-01.
    """

    REQUIRED_SECTIONS = [
        "# Sumário Executivo",
        "## Decisões Validadas",
        "## Issues Pendentes",
        "## Matriz de Risco",
        "## Veredito"
    ]

    def synthesize(self, board: ValidationBoard, idea_title: str, provider: ModelProvider) -> Dict[str, Any]:
        """
        Recebe o snapshot do board e gera o relatório via LLM.
        """
        snapshot = board.snapshot()
        prompt = self._build_prompt(snapshot, idea_title)
        
        try:
            report_text = provider.generate(prompt=prompt, role="synthesizer")
            if not report_text:
                return {"status": "error", "error": "LLM returned empty response", "sections_present": []}
            
            sections_present = self._validate_report(report_text)
            
            return {
                "status": "success",
                "report_markdown": report_text,
                "sections_present": sections_present,
                "source": "synthesizer"
            }
        except Exception as e:
            logger.error(f"Erro na síntese do relatório: {e}")
            return {
                "status": "error", 
                "error": str(e), 
                "report_markdown": None, 
                "sections_present": [],
                "source": "synthesizer"
            }

    def _build_prompt(self, board_snapshot: Dict[str, Any], idea_title: str) -> str:
        """
        Monta o prompt conforme o blueprint.
        """
        snapshot_json = json.dumps(board_snapshot, indent=2, ensure_ascii=False)
        
        return f"""Você é uma juíza técnica neutra. Sua única função é transformar os dados abaixo em um relatório estruturado.

REGRAS INVIOLÁVEIS:
1. Se uma informação não está em BOARD_SNAPSHOT, ela NÃO existe — não a invente.
2. Não expresse opinião pessoal. Registre apenas o que o debate produziu.
3. O relatório DEVE conter EXATAMENTE estas 5 seções, nesta ordem:
   - # Sumário Executivo
   - ## Decisões Validadas
   - ## Issues Pendentes
   - ## Matriz de Risco
   - ## Veredito
4. Se uma seção não tem dados, escreva: "(Nenhum registro nesta categoria)"
5. Responda APENAS com o relatório em Markdown. Nenhum texto antes ou depois.

IDEIA ANALISADA: {idea_title}

BOARD_SNAPSHOT:
{snapshot_json}
"""

    def _validate_report(self, report: str) -> List[str]:
        """
        Verifica quais seções obrigatórias estão presentes no texto.
        """
        present = []
        for section in self.REQUIRED_SECTIONS:
            if section in report:
                present.append(section)
        return present
