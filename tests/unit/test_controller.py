import pytest
import os
from unittest.mock import MagicMock, patch
from src.core.controller import Controller
from src.debate.debate_engine import DebateResult
from src.models.ollama_provider import OllamaMemoryError

def test_controller_run_returns_output_path(tmp_path):
    """Verifica se o controller retorna o caminho do relatório."""
    mock_engine = MagicMock()
    mock_engine.run_debate.return_value = DebateResult(
        final_proposal="Proposta",
        transcript=[],
        board_snapshot={},
        stats={"total_rounds": 1}
    )
    
    with patch("src.core.controller.DebateEngine", return_value=mock_engine), \
         patch("src.core.controller.SynthesizerAgent"), \
         patch("src.core.controller.ReportGenerator") as mock_gen, \
         patch("src.core.controller.OllamaProvider"):
        
        mock_gen_instance = mock_gen.return_value
        mock_gen_instance.generate.return_value = {
            "status": "success",
            "output_path": "test_report.md",
            "fallback_used": False,
            "sections_present": ["# S1", "## S2", "## S3", "## S4", "## S5"],
            "board_stats": {"total_issues": 0}
        }
        
        ctrl = Controller()
        # Assinatura atualizada: model_name agora é obrigatório no contrato de teste
        result = ctrl.run("Minha Ideia", model_name="llama3")
        
        assert result["status"] == "success"
        assert result["debate_rounds"] == 1

def test_controller_debug_flag_emits_to_stderr():
    """Garante que a flag debug imprime algo no stderr."""
    mock_engine = MagicMock()
    mock_engine.run_debate.return_value = DebateResult("P", [{"role": "user", "content": "hi"}], {}, {})
    
    with patch("src.core.controller.DebateEngine", return_value=mock_engine), \
         patch("src.core.controller.SynthesizerAgent"), \
         patch("src.core.controller.ReportGenerator"), \
         patch("src.core.controller.OllamaProvider"), \
         patch("sys.stderr.write") as mock_stderr:
        
        ctrl = Controller()
        ctrl.run("Ideia", model_name="llama3", debug=True)
        
        assert mock_stderr.called

def test_controller_model_name_passed_to_provider():
    """Verifica se o nome do modelo é passado corretamente."""
    with patch("src.core.controller.DebateEngine"), \
         patch("src.core.controller.SynthesizerAgent"), \
         patch("src.core.controller.ReportGenerator"), \
         patch("src.core.controller.OllamaProvider") as mock_provider:
        
        ctrl = Controller()
        ctrl.run("Ideia", model_name="ghost:latest", think=True)
        
        args, kwargs = mock_provider.call_args
        assert kwargs.get("model_name") == "ghost:latest"
        assert kwargs.get("think") is True
        assert kwargs.get("show_thinking") is True

def test_controller_think_false_passes_show_thinking_false():
    """BUG-B: Verifica se think=False desativa show_thinking."""
    with patch("src.core.controller.DebateEngine"), \
         patch("src.core.controller.SynthesizerAgent"), \
         patch("src.core.controller.ReportGenerator"), \
         patch("src.core.controller.OllamaProvider") as mock_provider:
        
        ctrl = Controller()
        ctrl.run("Ideia", model_name="m1", think=False)
        
        args, kwargs = mock_provider.call_args
        assert kwargs.get("think") is False
        assert kwargs.get("show_thinking") is False

def test_controller_returns_memory_error_dict():
    """Verifica se o controller captura OllamaMemoryError e retorna status adequado."""
    with patch("src.core.controller.OllamaProvider") as mock_provider:
        # Fazer o provider levantar erro de memória ao ser instanciado ou usado
        # No controller, o provider é instanciado em _get_provider
        mock_provider.side_effect = OllamaMemoryError("Sem RAM")
        
        ctrl = Controller()
        result = ctrl.run("Ideia", model_name="heavy-model")
        
        assert result["status"] == "memory_error"
        assert "Memória insuficiente" in result["error"]
