import pytest
import os
from src.core.controller import Controller
from tests.conftest import MockProvider

def test_controller_pipeline_integration(tmp_path):
    """Teste de integração ponta-a-ponta com MockProvider."""
    # Mock de respostas para Proponent (Expansion), Critic (Issues) e Synthesizer
    responses = {
        "proponent": "# 1. Visão Geral\nConteúdo\n## 2. Arquitetura\nConteúdo\n## 3. Fluxo\nConteúdo\n## 4. Stack\nConteúdo\n## 5. Desafios\nConteúdo\n## 6. Premissas\nConteúdo\n## 7. Próximos Passos\nConteúdo",
        "critic": "| ISS-001 | HIGH | SECURITY | Falha de Auth | Use JWT |",
        "synthesizer": "# Sumário Executivo\n## Decisões Validadas\n## Issues Pendentes\n## Matriz de Risco\n## Veredito"
    }
    
    # Criamos uma função que mapeia o prompt para o agente correto
    def mock_gen(prompt, role=None):
        if "juíza técnica neutra" in prompt:
            return responses["synthesizer"]
        if "expandir a ideia" in prompt.lower() or "proposta estruturada" in prompt:
            return responses["proponent"]
        if "debate técnico" in prompt.lower() or "crítica" in prompt.lower():
            return responses["critic"]
        return "Resposta genérica"

    provider = MockProvider(responses=mock_gen)
    
    # Injetamos o provider no pipeline (precisaremos de um patch no Controller para usar este provider)
    with patch("src.core.controller.OllamaProvider", return_value=provider):
        ctrl = Controller()
        # Forçamos o output_path para o tmp_path
        with patch.object(ctrl, "_get_output_path", return_value=str(tmp_path / "final_report.md")):
            result = ctrl.run("Startup de IA", model_name="mock-model")
            
            assert result["status"] == "success"
            assert os.path.exists(result["output_path"])
            with open(result["output_path"], "r", encoding="utf-8") as f:
                content = f.read()
                assert "Decisões Validadas" in content
                assert "Veredito" in content

from unittest.mock import patch
