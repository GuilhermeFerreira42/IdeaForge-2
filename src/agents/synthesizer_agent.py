import json
import logging
from typing import Dict, Any, List, Optional

from src.models.model_provider import ModelProvider
from src.core.validation_board import ValidationBoard

logger = logging.getLogger(__name__)

class SynthesizerAgent:
    """
    Juíza neutra que converte o estado do ValidationBoard em um relatório Markdown.
    Responsabilidade: W3-01.
    """

    DEFAULT_SECTIONS = [
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
        profile = board.get_domain_profile()
        snapshot = board.snapshot()
        prompt = self._build_prompt(snapshot, idea_title, profile)
        
        # Determinar seções requeridas dinamicamente
        required_sections = self.DEFAULT_SECTIONS
        if profile and profile.report_sections:
            required_sections = [s.title for s in profile.report_sections]
            # Adiciona Veredito se não estiver presente no profile (invariante)
            if not any("Veredito" in s for s in required_sections):
                required_sections.append("## Veredito")

        try:
            report_text = provider.generate(prompt=prompt, role="synthesizer")
            if not report_text:
                return {"status": "error", "error": "LLM returned empty response", "sections_present": []}
            
            sections_present = self._validate_report(report_text, required_sections)
            
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

    def _build_prompt(self, board_snapshot: Dict[str, Any], idea_title: str, profile: Optional[Any] = None) -> str:
        """
        Monta o prompt conforme o blueprint.
        """
        snapshot_json = json.dumps(board_snapshot, indent=2, ensure_ascii=False)
        domain = profile.domain.upper() if profile else "GENERIC"
        
        sections_str = "\n".join([f"- {s}" for s in self.DEFAULT_SECTIONS])
        if profile and profile.report_sections:
            sections_str = "\n".join([f"- {s.title}" for s in profile.report_sections])
            if "Veredito" not in sections_str:
                sections_str += "\n- ## Veredito"

        return f"""Você é uma juíza técnica neutra especializada no domínio {domain}. 
Sua única função é transformar os dados abaixo em um relatório estruturado e profissional.

REGRAS INVIOLÁVEIS:
1. Se uma informação não está em BOARD_SNAPSHOT, ela NÃO existe — não a invente.
   ATENÇÃO: O BOARD_SNAPSHOT contém os dados reais do debate — issues encontrados, decisões tomadas e pressupostos identificados. USE esses dados para preencher as seções. Um board não-vazio NUNCA deve gerar "(Nenhum registro)" em Issues ou Decisões.
2. Não expresse opinião pessoal. Registre apenas o que o debate produziu.
3. O relatório DEVE conter EXATAMENTE estas seções, nesta ordem:
{sections_str}
4. Se uma seção não tem dados, escreva: "(Nenhum registro nesta categoria)"
5. Responda APENAS com o relatório em Markdown. Nenhum texto antes ou depois.

IDEIA ANALISADA: {idea_title}

BOARD_SNAPSHOT:
{snapshot_json}
"""

    def _validate_report(self, report: str, required_sections: List[str]) -> List[str]:
        """
        Verifica quais seções obrigatórias estão presentes no texto.
        """
        present = []
        for section in required_sections:
            if section in report:
                present.append(section)
        return present
