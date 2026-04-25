import pytest
import os
from src.core.report_generator import ReportGenerator
from src.agents.synthesizer_agent import SynthesizerAgent
from src.core.validation_board import ValidationBoard, IssueRecord, DecisionRecord
from tests.conftest import MockProvider

class MockSynthesizer:
    def __init__(self, fail=False, invalid=False):
        self.fail = fail
        self.invalid = invalid
    
    def synthesize(self, board, title, provider):
        if self.fail:
            return {"status": "error", "error": "LLM Failed", "sections_present": []}
        if self.invalid:
            return {
                "status": "success", 
                "report_markdown": "# Only One Section", 
                "sections_present": ["# Only One Section"]
            }
        return {
            "status": "success",
            "report_markdown": "# Sumário Executivo\n## Decisões Validadas\n## Issues Pendentes\n## Matriz de Risco\n## Veredito",
            "sections_present": ["# Sumário Executivo", "## Decisões Validadas", "## Issues Pendentes", "## Matriz de Risco", "## Veredito"]
        }

def test_report_generator_success_path(tmp_path):
    """Verifica caminho feliz: síntese OK."""
    board = ValidationBoard()
    synth = MockSynthesizer()
    gen = ReportGenerator()
    out_file = tmp_path / "report.md"
    
    result = gen.generate(board, synth, "Ideia Teste", str(out_file), None)
    
    assert result["status"] == "success"
    assert result["fallback_used"] is False
    assert os.path.exists(out_file)

def test_report_generator_fallback_on_llm_error(tmp_path):
    """Verifica fallback quando o Synthesizer retorna erro."""
    board = ValidationBoard()
    board.add_issue(IssueRecord("ISS-99", "HIGH", "SEC", "Critical"))
    synth = MockSynthesizer(fail=True)
    gen = ReportGenerator()
    out_file = tmp_path / "fallback_error.md"
    
    result = gen.generate(board, synth, "Erro Teste", str(out_file), None)
    
    assert result["status"] == "success"
    assert result["fallback_used"] is True
    assert result["source"] == "fallback"
    with open(out_file, "r", encoding="utf-8") as f:
        content = f.read()
        assert "ISS-99" in content
        assert "Fallback" in content
        assert "SynthesizerAgent falhou" in content

def test_report_generator_fallback_on_invalid_report(tmp_path):
    """Verifica fallback quando o relatório tem seções insuficientes (< 3)."""
    board = ValidationBoard()
    synth = MockSynthesizer(invalid=True)
    gen = ReportGenerator()
    out_file = tmp_path / "fallback_invalid.md"
    
    result = gen.generate(board, synth, "Invalido", str(out_file), None)
    
    assert result["fallback_used"] is True

def test_fallback_dump_preserves_all_records():
    """Garante que o dump contém todos os IDs do board."""
    board = ValidationBoard()
    board.add_issue(IssueRecord("ISS-01", "LOW", "CAT", "Desc"))
    board.add_decision(DecisionRecord("DEC-01", "Desc"))
    
    gen = ReportGenerator()
    dump = gen._fallback_dump(board, "Dump Test")
    
    assert "ISS-01" in dump
    assert "DEC-01" in dump
    assert "Dump Test" in dump

def test_fallback_file_size_nonzero(tmp_path):
    """Verifica se o arquivo de fallback tem conteúdo."""
    board = ValidationBoard()
    gen = ReportGenerator()
    out_file = tmp_path / "nonzero.md"
    
    gen._persist("conteudo", str(out_file))
    
    assert os.path.getsize(out_file) > 0
