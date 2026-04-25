from abc import ABC, abstractmethod
from typing import NamedTuple, Optional


class GenerationResult(NamedTuple):
    """Resultado estruturado de uma geração de LLM."""
    content: str          # Resposta final limpa
    thinking: str         # Raciocínio capturado (vazio se não disponível)
    raw: str              # Output bruto completo


class ModelProvider(ABC):
    """
    Interface base para todos os provedores de LLM (Local e Cloud).
    """

    @abstractmethod
    def generate(self, prompt: str, context: list = None, 
                 role: str = "user", max_tokens: Optional[int] = None) -> str:
        """
        Gera texto baseado no prompt e contexto da conversa.
        Retorna string de conteúdo limpa.
        """
        pass

    def generate_with_thinking(self, prompt: str, context: list = None, 
                                role: str = "user", 
                                max_tokens: Optional[int] = None) -> GenerationResult:
        """
        Gera texto e retorna resultado estruturado com raciocínio separado.
        A implementação padrão envolve generate() para provedores que não suportam thinking.
        """
        content = self.generate(prompt, context, role, max_tokens=max_tokens)
        return GenerationResult(content=content, thinking="", raw=content)
