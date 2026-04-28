import pytest
import os
import requests
from src.core.controller import Controller
from src.config.settings import OLLAMA_ENDPOINT, DEFAULT_MODEL

def is_ollama_online():
    """Checa se o Ollama está rodando localmente."""
    try:
        response = requests.get(OLLAMA_ENDPOINT.replace("/generate", "/tags"), timeout=2)
        return response.status_code == 200
    except:
        return False

@pytest.mark.skipif(not is_ollama_online(), reason="Ollama não detectado localmente.")
def test_smoke_full_pipeline():
    """Executa o pipeline completo contra o Ollama real."""
    idea = "Sistema de delivery com drones para farmácias"
    ctrl = Controller()
    
    result = ctrl.run(idea, model_name="llama3.2:1b", debug=True)
    
    assert result["status"] == "success"
    assert "output_path" in result
    report_path = result["output_path"]
    assert os.path.exists(report_path)
    
    # Cleanup
    if os.path.exists(report_path):
        os.remove(report_path)

def test_controller_initialization():
    """Verifica se o controller e seus componentes básicos carregam sem erro."""
    ctrl = Controller()
    assert ctrl.tracker is not None
    assert ctrl.synthesizer is not None
