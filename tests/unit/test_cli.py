import pytest
import sys
from unittest.mock import patch, MagicMock
from src.cli.main import main
from src.models.ollama_provider import OllamaServiceError

def test_cli_full_interactive_flow(capsys):
    """Testa o fluxo interativo completo: lista modelos -> escolhe -> entra ideia -> sucesso."""
    models = [{"name": "m1:latest", "size": 1000000000}]
    
    with patch("src.cli.main.OllamaProvider.list_available_models", return_value=models), \
         patch("src.cli.main.OllamaProvider.check_thinking_support", return_value=False), \
         patch("src.cli.main.Controller") as mock_ctrl_class, \
         patch("builtins.input", side_effect=["1", "Minha Ideia"]), \
         patch.object(sys, 'argv', ['main.py']):
        
        mock_ctrl = mock_ctrl_class.return_value
        mock_ctrl.run.return_value = {
            "status": "success", 
            "output_path": "report.md",
            "debate_rounds": 1,
            "issues_total": 0,
            "model_used": "m1:latest"
        }
        
        main()
        
        # Verifica se chamou controller com o modelo escolhido
        mock_ctrl.run.assert_called_with(idea="Minha Ideia", model_name="m1:latest", think=False, debug=False)
        captured = capsys.readouterr()
        assert "PIPELINE CONCLUIDO" in captured.out

def test_cli_loops_on_memory_error(capsys):
    """Verifica se a CLI volta para a seleção de modelo em caso de erro de memória."""
    models = [{"name": "heavy", "size": 999999}, {"name": "light", "size": 1}]
    
    with patch("src.cli.main.OllamaProvider.list_available_models", return_value=models), \
         patch("src.cli.main.OllamaProvider.check_thinking_support", return_value=False), \
         patch("src.cli.main.Controller") as mock_ctrl_class, \
         patch("builtins.input", side_effect=["1", "Ideia", "2", "Ideia"]), \
         patch.object(sys, 'argv', ['main.py']):
        
        mock_ctrl = mock_ctrl_class.return_value
        # Primeira chamada retorna memory_error, segunda sucesso
        mock_ctrl.run.side_effect = [
            {"status": "memory_error", "error": "RAM low"},
            {"status": "success", "output_path": "ok.md", "debate_rounds": 1, "issues_total": 0, "model_used": "light"}
        ]
        
        main()
        
        captured = capsys.readouterr()
        assert "Memoria insuficiente" in captured.out
        # Verificamos que o controller foi chamado duas vezes (uma para cada escolha de modelo)
        assert mock_ctrl.run.call_count == 2

def test_cli_skip_interactive_if_flags_present():
    """Se passar --idea e --model, pula o input()."""
    with patch("src.cli.main.Controller") as mock_ctrl_class, \
         patch("builtins.input") as mock_input, \
         patch.object(sys, 'argv', ['main.py', '--idea', 'Quick', '--model', 'm1']):
        
        mock_ctrl = mock_ctrl_class.return_value
        mock_ctrl.run.return_value = {"status": "success", "output_path": "x.md", "debate_rounds": 1, "issues_total": 0, "model_used": "m1"}
        
        main()
        
        mock_input.assert_not_called()
        mock_ctrl.run.assert_called_with(idea="Quick", model_name="m1", think=False, debug=False)

def test_cli_service_offline_exits(capsys):
    """Encerra com erro se o Ollama estiver offline."""
    with patch("src.cli.main.OllamaProvider.list_available_models", side_effect=OllamaServiceError("Offline")), \
         patch.object(sys, 'argv', ['main.py']):
        
        with pytest.raises(SystemExit) as excinfo:
            main()
        
        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        assert "Erro no servico Ollama" in captured.out
