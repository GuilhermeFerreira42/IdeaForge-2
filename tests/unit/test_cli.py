import pytest
import sys
from unittest.mock import patch, MagicMock
from src.cli.main import main

def test_cli_help_output(capsys):
    """Verifica se -h funciona."""
    with patch.object(sys, 'argv', ['main.py', '-h']):
        with pytest.raises(SystemExit):
            main()
    captured = capsys.readouterr()
    assert "--idea" in captured.out
    assert "--model" in captured.out

def test_cli_calls_controller_with_correct_args():
    """Garante que os flags da CLI chegam no Controller."""
    with patch("src.cli.main.Controller") as mock_ctrl_class, \
         patch.object(sys, 'argv', ['main.py', '--idea', 'Test Idea', '--model', 'm1', '--debug']):
        
        mock_ctrl = mock_ctrl_class.return_value
        mock_ctrl.run.return_value = {
            "status": "success", 
            "output_path": "path",
            "debate_rounds": 2,
            "issues_total": 5
        }
        
        main()
        
        mock_ctrl.run.assert_called_with(idea="Test Idea", model_override="m1", debug=True)

def test_cli_handles_error_from_controller(capsys):
    """Verifica exibição de erro quando o controller falha."""
    with patch("src.cli.main.Controller") as mock_ctrl_class, \
         patch.object(sys, 'argv', ['main.py', '--idea', 'Bad Idea']):
        
        mock_ctrl = mock_ctrl_class.return_value
        mock_ctrl.run.return_value = {"status": "error", "error": "Something went wrong"}
        
        with pytest.raises(SystemExit) as excinfo:
            main()
        
        assert excinfo.value.code == 1
        captured = capsys.readouterr()
        assert "ERRO" in captured.out
        assert "Something went wrong" in captured.out
