import pytest
import os
from unittest.mock import MagicMock, patch
from src.core.controller import Controller
from src.debate.debate_engine import DebateResult

def test_controller_run_returns_output_path(tmp_path):
    """Verifica se o controller retorna o caminho do relatório."""
    mock_engine = MagicMock()
    mock_engine.run_debate.return_value = DebateResult(
        final_proposal="Proposta",
        transcript=[],
        board_snapshot={},
        stats={"total_rounds": 1}
    )
    
    # Mocking components to avoid real LLM/file I/O dependencies here
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
        result = ctrl.run("Minha Ideia")
        
        assert result["status"] == "success"
        assert "test_report.md" in result["output_path"]
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
        ctrl.run("Ideia", debug=True)
        
        # Verifica se stderr.write foi chamado (para transcrito ou board)
        assert mock_stderr.called

def test_controller_model_override_passed_to_provider():
    """Verifica se o override de modelo é respeitado."""
    with patch("src.core.controller.DebateEngine"), \
         patch("src.core.controller.SynthesizerAgent"), \
         patch("src.core.controller.ReportGenerator"), \
         patch("src.core.controller.OllamaProvider") as mock_provider:
        
        ctrl = Controller()
        ctrl.run("Ideia", model_override="ghost:latest")
        
        # O provedor deve ser instanciado com o modelo override
        args, kwargs = mock_provider.call_args
        assert kwargs.get("model") == "ghost:latest"
