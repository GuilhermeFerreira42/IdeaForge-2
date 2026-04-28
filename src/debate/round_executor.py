import re
import logging
import hashlib
from dataclasses import dataclass
from typing import List, Optional

from src.models.model_provider import ModelProvider
from src.core.validation_board import ValidationBoard
from src.debate.debate_state_tracker import DebateStateTracker
from src.debate.context_builder import ContextBuilder
from src.agents.proponent_agent import ProponentAgent
from src.agents.critic_agent import CriticAgent
from src.core import prompt_templates

logger = logging.getLogger(__name__)

@dataclass
class RoundResult:
    """Resultado processado de um turno de debate."""
    raw_text: str
    parsing_succeeded: bool
    new_issue_count: int
    updated_proposal: Optional[str] = None

class RoundExecutor:
    """
    Executa turnos isolados do debate, coordenando Agente + Tracker + Patches.
    """
    
    CANONICAL_HEADINGS = [
        "Visão Geral",
        "Arquitetura de Componentes",
        "Fluxo de Dados Principal",
        "Stack Tecnológica Sugerida",
        "Principais Desafios Técnicos",
        "Premissas de Implementação",
        "Próximos Passos Imediatos"
    ]

    def __init__(self, provider: ModelProvider, board: ValidationBoard, 
                 tracker: DebateStateTracker, builder: ContextBuilder):
        self.provider = provider
        self.board = board
        self.tracker = tracker
        self.builder = builder
        self.proponent = ProponentAgent(provider)
        self.critic = CriticAgent(provider)

    def _canonicalize_table(self, text: str) -> str:
        """
        Normaliza tabelas Markdown para o parser v1 (L1/L2) [COR-11].
        - Adiciona ID único baseado em hash para evitar deduplicação indevida (HF02).
        - Mapeia severidades/categorias PT->EN.
        """
        lines = text.split('\n')
        new_lines = []
        for line in lines:
            if '|' in line and '---' not in line:
                # Tenta detectar se é uma linha de dados (ex: | HIGH | ...)
                cols = [c.strip() for c in line.split('|') if c.strip()]
                if len(cols) == 4: # Formato Novo: Sev | Cat | Desc | Sug
                    sev = prompt_templates.PT_EN_NORMALIZATION_MAP.get(cols[0].upper(), cols[0].upper())
                    cat = prompt_templates.PT_EN_NORMALIZATION_MAP.get(cols[1].upper(), cols[1].upper())
                    description = cols[2]
                    suggestion = cols[3]
                    desc_sug = f"{description} (Sugere-se: {suggestion})"
                    
                    # BUG-A FIX: Gerar ID único por linha usando hash da descrição
                    unique_id = f"ISS-{abs(hash(description[:100])) % 9000 + 1000}"
                    
                    # Converte para formato compatível com Tracker Onda 1: | ISS-XX | SEV | CAT | DESC |
                    new_lines.append(f"| {unique_id} | {sev} | {cat} | {desc_sug} |")
                    continue
            new_lines.append(line)
        return "\n".join(new_lines)

    def _detect_subextraction(self, text: str, extracted_count: int) -> bool:
        """
        Heurística para detectar se o parser falhou em extrair algo substancial [COR-14].
        """
        if extracted_count > 0:
            return True
        
        # Se texto for curto, 0 issues pode ser legítimo
        if len(text.strip()) < 200:
            return True
            
        # Se for longo e não houver issues extraídos, checar keywords de negatividade
        keywords = ["risco", "problema", "falha", "erro", "inconsistência", "grave"]
        if any(k in text.lower() for k in keywords):
            logger.warning("[RoundExecutor] Resposta longa com keywords de risco mas 0 issues extraídos. Falha de parsing suspeita.")
            return False
            
        return True

    def execute_critic_round(self, current_proposal: str, last_defense: str, round_num: int) -> RoundResult:
        """Executa turno do Critic."""
        prompt = self.builder.build_critique_prompt(current_proposal, last_defense)
        raw_text = self.critic.review(prompt)
        
        # GUARDA DE SEGURANÇA: Evitar falsa convergência por falhas de API
        if len(raw_text.strip()) < 50:
            logger.error(f"[RoundExecutor] Resposta do Crítico extremamente curta ({len(raw_text)} chars). Falha de API ou Prompt?")
            return RoundResult(
                raw_text=f"[FAILED_ROUND_SHORT_RESPONSE_{round_num}]",
                parsing_succeeded=False,
                new_issue_count=-1
            )
        
        # Canonicalizar antes do tracker
        processed_text = self._canonicalize_table(raw_text)
        
        new_ids = self.tracker.extract_issues_from_critique(processed_text, round_num, self.board)
        
        succeeded = self._detect_subextraction(raw_text, len(new_ids))
        issue_count = len(new_ids) if succeeded else -1
        
        return RoundResult(
            raw_text=raw_text,
            parsing_succeeded=succeeded,
            new_issue_count=issue_count
        )

    def execute_defense_round(self, current_proposal: str, last_critique: str, round_num: int) -> RoundResult:
        """Executa turno do Proponent."""
        prompt = self.builder.build_defense_prompt(current_proposal, last_critique)
        raw_text = self.proponent.defend(prompt)
        
        # GUARDA DE SEGURANÇA: Evitar corrupção do texto por falhas de API
        if len(raw_text.strip()) < 50:
            logger.error(f"[RoundExecutor] Resposta do Proponente extremamente curta ({len(raw_text)} chars). Mantendo proposta atual.")
            return RoundResult(
                raw_text=f"[FAILED_DEFENSE_SHORT_RESPONSE_{round_num}]",
                parsing_succeeded=False,
                new_issue_count=0,
                updated_proposal=current_proposal
            )
            
        updated_proposal = self.apply_defense_patches(current_proposal, raw_text)
        
        # Tracker extrai resoluções
        self.tracker.extract_resolutions_from_defense(raw_text, round_num, self.board)
        
        return RoundResult(
            raw_text=raw_text,
            parsing_succeeded=True,
            new_issue_count=0,
            updated_proposal=updated_proposal
        )

    def apply_defense_patches(self, current_proposal: str, defense_text: str) -> str:
        """
        Aplica patches de melhoria na proposta arquitetural baseada na defesa.
        """
        if "## Melhorias Propostas" not in defense_text:
            return current_proposal
            
        # Extrair tabela de patches
        pattern = r'\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
        matches = re.findall(pattern, defense_text)
        
        new_proposal = current_proposal
        for section_name, change, justification in matches:
            section_name = section_name.strip()
            if section_name.lower() in ["seção", "area", "área"]: continue # Header
            
            # Match fuzzy de heading
            best_match = None
            for h in self.CANONICAL_HEADINGS:
                # Normalização agressiva para match
                h_norm = h.lower().replace(" ", "")
                s_norm = section_name.lower().replace(" ", "").replace("#", "").split(".")[-1]
                if s_norm in h_norm or h_norm in s_norm:
                    best_match = h
                    break
            
            if best_match:
                # Tentar substituir conteúdo da seção
                # Regex procura do heading (podendo ter números ex: # 1. Visão) até o próximo heading
                section_pattern = rf"(#+\s*.*?{re.escape(best_match)}.*?\n)(.*?)(?=\n#+|$)"
                match_obj = re.search(section_pattern, new_proposal, re.DOTALL | re.IGNORECASE)
                
                if match_obj:
                    header = match_obj.group(1)
                    # Append da mudança ao final da seção para manter rastro
                    improved_section = f"{header}{match_obj.group(2).strip()}\n\n> **MELHORIA APLICADA:** {change.strip()}\n"
                    new_proposal = new_proposal.replace(match_obj.group(0), improved_section)
        
        return new_proposal
