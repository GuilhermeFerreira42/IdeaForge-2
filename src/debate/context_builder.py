from src.core.validation_board import ValidationBoard
from src.core import prompt_templates

class ContextBuilder:
    """
    Componente responsável por montar prompts truncados e contextualizados.
    Garante o limite rígido de 3000 caracteres [COR-13].
    """
    
    BUDGETS = {
        "system": 600,
        "proposal": 800,
        "issues": 600,
        "response": 700,
        "decisions": 300
    }

    def __init__(self, board: ValidationBoard):
        self.board = board

    def _truncate(self, text: str, limit: int) -> str:
        """Truncamento determinístico com elipse se necessário."""
        if len(text) <= limit:
            return text
        return text[:limit-3] + "..."

    def build_defense_prompt(self, current_proposal: str, last_critique: str, last_defense: str = "") -> str:
        """
        Monta o prompt para o ProponentAgent em modo defesa.
        """
        # 1. System Prompt (limit 600)
        system = self._truncate(prompt_templates.DEFENSE_SYSTEM_PROMPT, self.BUDGETS["system"])
        
        # 2. Issues Abertos (limit 600)
        issues_text = self.board.get_issues_for_proponent_prompt()
        issues = self._truncate(issues_text, self.BUDGETS["issues"])
        
        # 3. Decisões Validadas (limit 300)
        decisions_text = self.board.get_validated_decisions_prompt()
        decisions = self._truncate(decisions_text, self.BUDGETS["decisions"])
        
        # 4. Proposta Vigente (limit 800)
        proposal = self._truncate(current_proposal, self.BUDGETS["proposal"])
        
        # 5. Última Crítica/Resposta (limit 700)
        critique = self._truncate(last_critique, self.BUDGETS["response"])
        
        # Montagem Final
        prompt_parts = [
            system,
            "\n### CONTEXTO DO DEBATE",
            f"\nISSUES ABERTOS:\n{issues}",
            f"\nDECISÕES VALIDADAS:\n{decisions}",
            f"\nPROPOSTA VIGENTE:\n{proposal}",
            f"\nÚLTIMA CRÍTICA RECEBIDA:\n{critique}"
        ]
        
        if last_defense:
            defense = self._truncate(last_defense, 300) # Espaço extra se houver
            prompt_parts.append(f"\nSUA ÚLTIMA DEFESA:\n{defense}")

        final_prompt = "\n".join(prompt_parts)
        
        # Hard limit de segurança
        if len(final_prompt) > 3000:
            return final_prompt[:2997] + "..."
            
        return final_prompt

    def build_critique_prompt(self, current_proposal: str, last_defense: str) -> str:
        """
        Monta o prompt para o CriticAgent.
        """
        system = self._truncate(prompt_templates.CRITIQUE_SYSTEM_PROMPT, self.BUDGETS["system"])
        issues = self._truncate(self.board.get_open_issues_for_critic_prompt(), self.BUDGETS["issues"])
        decisions = self._truncate(self.board.get_validated_decisions_prompt(), self.BUDGETS["decisions"])
        proposal = self._truncate(current_proposal, self.BUDGETS["proposal"])
        defense = self._truncate(last_defense, self.BUDGETS["response"])
        
        prompt_parts = [
            system,
            f"\nISSUES ABERTOS (NÃO REPETIR):\n{issues}",
            f"\nDECISÕES VALIDADAS:\n{decisions}",
            f"\nPROPOSTA VIGENTE:\n{proposal}",
            f"\nÚLTIMA DEFESA DO PROPONENTE:\n{defense}"
        ]
        
        return "\n".join(prompt_parts)[:3000]
