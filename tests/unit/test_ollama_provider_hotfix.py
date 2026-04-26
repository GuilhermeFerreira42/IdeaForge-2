import pytest
import requests
import subprocess
from unittest.mock import patch, MagicMock
from src.models.ollama_provider import OllamaProvider, OllamaMemoryError, OllamaServiceError

def test_list_models_success():
    """Verifica se list_available_models retorna a lista formatada quando o Ollama responde OK."""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "models": [
            {"name": "llama3:latest", "details": {"parameter_size": "8B"}, "size": 5000000000},
            {"name": "qwen2.5:7b", "details": {"parameter_size": "7B"}, "size": 4000000000}
        ]
    }
    mock_response.raise_for_status = MagicMock()

    with patch("requests.get", return_value=mock_response):
        models = OllamaProvider.list_available_models()
        assert len(models) == 2
        assert models[0]["name"] == "llama3:latest"
        assert "8B" in models[0]["details"]["parameter_size"]

def test_list_models_offline():
    """Verifica se dispara OllamaServiceError quando o serviço está offline."""
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(OllamaServiceError) as excinfo:
            OllamaProvider.list_available_models()
        assert "Ollama está offline" in str(excinfo.value)

def test_check_thinking_support_true():
    """Verifica detecção de thinking quando presente no output do show."""
    mock_cp = MagicMock()
    mock_cp.stdout = "Capabilities: thinking, generative\nParameter size: 8B"
    mock_cp.returncode = 0
    
    with patch("subprocess.run", return_value=mock_cp):
        assert OllamaProvider.check_thinking_support("deepseek-r1") is True

def test_check_thinking_support_false():
    """Verifica detecção de ausência de thinking."""
    mock_cp = MagicMock()
    mock_cp.stdout = "Capabilities: generative\n"
    mock_cp.returncode = 0
    
    with patch("subprocess.run", return_value=mock_cp):
        assert OllamaProvider.check_thinking_support("llama3") is False

def test_generate_raises_memory_error():
    """Verifica se o erro de memória do Ollama é capturado e transformado em exceção tipada."""
    provider = OllamaProvider(model_name="heavy-model")
    
    # Simular stream retornando primeiro chunk com erro de memória
    mock_line = b'{"error": "model requires more system memory than is available"}'
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = iter([mock_line])
    mock_response.raise_for_status = MagicMock()

    with patch("requests.post", return_value=mock_response):
        with pytest.raises(OllamaMemoryError):
            provider.generate("Qualquer coisa")

def test_generate_raises_service_error_on_generic_error():
    """Verifica se erros genéricos do Ollama também são capturados."""
    provider = OllamaProvider(model_name="buggy-model")
    
    mock_line = b'{"error": "something went wrong on the server side"}'
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = iter([mock_line])
    
    with patch("requests.post", return_value=mock_response):
        with pytest.raises(OllamaServiceError):
            provider.generate("Qualquer coisa")
