import pytest
from src.debate.debate_engine import DebateEngine
from src.core.validation_board import ValidationBoard
from src.debate.debate_state_tracker import DebateStateTracker
from src.debate.context_builder import ContextBuilder
from tests.conftest import MockProvider

def test_full_debate_natural_convergência():
    """Simula um debate completo que converge após alguns rounds."""
    board = ValidationBoard()
    tracker = DebateStateTracker()
    builder = ContextBuilder(board=board)
    
    # Mock de respostas
    def generator_factory(prompt):
        if "ESTRUTURA OBRIGATÓRIA" in prompt:
            return "# 1. Visão Geral\nProposta inicial"
        if "Você é o Agente Crítico" in prompt:
            # Check for empty issues indication
            if "Nenhum issue aberto" in prompt:
                return "## Novos Issues Encontrados\n| HIGH | SECURITY | Falha X | Corrigir |"
            return "## Novos Issues Encontrados\nNenhum problema novo."
        if "Você é o Agente Proponente defendendo" in prompt:
            return "## Pontos Aceitos\nAceito ISS-000. ## Melhorias Propostas\n| Visão Geral | Modificado | Justifica |"
        return "Mock response"

    provider = MockProvider(responses=generator_factory)
    engine = DebateEngine(provider=provider, board=board, tracker=tracker, builder=builder)
    
    result = engine.run_debate("Criação de um sistema de cache")
    
    assert result.stats["total_rounds"] >= 2
    # Agora deve ter aplicado o patch
    assert "Modificado" in result.final_proposal
    assert "convergência" in result.stats["stop_reason"].lower()

def test_debate_forced_stop_max_rounds():
    """Garante parada forçada em MAX_ROUNDS."""
    board = ValidationBoard()
    tracker = DebateStateTracker()
    builder = ContextBuilder(board=board)
    
    # Gerador que sempre levanta issues muito diferentes para evitar convergência Jaccard
    count = 0
    def infinite_issues(prompt):
        nonlocal count
        if "ESTRUTURA OBRIGATÓRIA" in prompt: return "# Proposta"
        if "Você é o Agente Crítico" in prompt:
            count += 1
            # Gerar texto aleatório longo para baixar Jaccard
            return f"## Novos Issues Encontrados\n| MED | COMPLETENESS | Falta-{count} | " + "X" * (count * 10)
        if "Você é o Agente Proponente" in prompt: return "Defesa técnica " + "Y" * (count * 10)
        return "..."

    provider = MockProvider(responses=infinite_issues)
    # Set max_rounds=3 e min_rounds=1 para garantir que rodará exatamente 3 rounds
    engine = DebateEngine(provider=provider, board=board, tracker=tracker, builder=builder, max_rounds=3, min_rounds=1)
    
    result = engine.run_debate("Teste")
    
    assert result.stats["total_rounds"] == 3
    assert "MAX_ROUNDS" in result.stats["stop_reason"]

def test_debate_handles_parsing_failure_retry():
    """Verifica se falha de parsing impede STOP prematuro."""
    board = ValidationBoard()
    tracker = DebateStateTracker()
    builder = ContextBuilder(board=board)
    
    calls = 0
    def parsing_failure_then_success(prompt):
        nonlocal calls
        if "ESTRUTURA OBRIGATÓRIA" in prompt: return "# Proposta"
        if "Você é o Agente Crítico" in prompt:
            calls += 1
            if calls == 1:
                return "Risco grave detectado! [Sem tabela e bem longo para acionar detecção de subextração]" + "z" * 300
            return "## Novos Issues Encontrados\n| HIGH | SECURITY | Falha | Corrigir |"
        return "Ok"

    provider = MockProvider(responses=parsing_failure_then_success)
    # Min rounds 1 para não forçar continuação por limite inferior
    engine = DebateEngine(provider=provider, board=board, tracker=tracker, builder=builder, min_rounds=1)
    
    result = engine.run_debate("Teste")
    
    # Se o primeiro round falha no parsing (count -1), o orquestrador não vê convergência
    assert calls > 1
