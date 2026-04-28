import pytest
from unittest.mock import MagicMock
from src.core.domain_context_builder import DomainContextBuilder, DOMAIN_FALLBACKS
from src.core.domain_profile import DomainProfile

def test_apply_fallback_for_generic():
    provider = MagicMock()
    builder = DomainContextBuilder(provider)
    profile = builder.build("Ideia vaga", "generic")
    
    assert profile.domain == "generic"
    assert profile.source == "fallback"
    # Verificar se as 7 seções universais estão lá
    section_ids = [s.id for s in profile.expansion_sections]
    expected = ["PROBLEMA", "PUBLICO_STAKEHOLDERS", "SOLUCAO_TESE", "OPERACAO_IMPLEMENTACAO", "RISCOS", "PREMISSAS", "CRITERIOS_SUCESSO"]
    for e in expected:
        assert e in section_ids

def test_build_with_llm_success():
    provider = MagicMock()
    # Mock return JSON valid match with contracts
    provider.generate.return_value = '{"expansion_sections": [{"id": "TEST", "title": "Test", "instruction": "Test"}], "validation_dimensions": [{"id": "DIM", "display_name": "Dim", "description": "Desc", "spawn_hint": "Hint"}]}'
    
    builder = DomainContextBuilder(provider)
    profile = builder.build("SaaS de Logística", "business")
    
    assert profile.source == "llm"
    assert profile.get_section_by_id("TEST").title == "Test"

def test_extract_json_from_markdown():
    provider = MagicMock()
    # Mock MD wrapped JSON
    provider.generate.return_value = 'Aqui está o JSON:\n```json\n{"expansion_sections": [], "validation_dimensions": []}\n```'
    builder = DomainContextBuilder(provider)
    profile = builder.build("Ideia", "software")
    assert profile.source == "llm"

def test_extract_json_caminho3_boundary_detection():
    """W5Q-01: boundary detection captura JSON embrulhado em prosa."""
    builder = DomainContextBuilder(provider=None)
    response = 'Claro! Aqui está o JSON: {"key": "value", "list": [1, 2]} Espero que ajude.'
    result = builder._extract_json(response)
    assert result == {"key": "value", "list": [1, 2]}

def test_extract_json_caminho3_com_texto_antes_e_depois():
    """W5Q-01: boundary detection ignora texto antes e depois do JSON."""
    builder = DomainContextBuilder(provider=None)
    response = 'Texto antes\n{"a": 1, "b": [{"c": 2}]}\nTexto depois'
    result = builder._extract_json(response)
    assert result is not None
    assert result["a"] == 1

def test_extract_json_retorna_none_se_todos_caminhos_falham():
    """W5Q-01: retorna None se resposta não contém JSON válido."""
    builder = DomainContextBuilder(provider=None)
    result = builder._extract_json("Texto sem JSON nenhum aqui.")
    assert result is None

def test_extract_json_nao_lanca_excecao():
    """W5Q-01: _extract_json nunca propaga exceção."""
    builder = DomainContextBuilder(provider=None)
    # JSON mal formado com boundary parcial
    result = builder._extract_json('{"key": "value", ERRO}')
    assert result is None  # Não lança, retorna None

def test_build_with_llm_usa_max_tokens_800(monkeypatch):
    """W5Q-01: generate() é chamado com max_tokens=800, não 600."""
    call_log = {}
    class MockProv:
        def generate(self, prompt, max_tokens, role, show_thinking=None):
            call_log['max_tokens'] = max_tokens
            return '{"expansion_sections": [], "validation_dimensions": []}'
    builder = DomainContextBuilder(provider=MockProv())
    builder._build_with_llm("ideia", "software")
    assert call_log['max_tokens'] == 800

def test_hybrid_fallback_secoes_obrigatorias():
    """W5Q-02: Fallback hybrid deve conter as 8 seções obrigatórias."""
    builder = DomainContextBuilder(provider=None)
    profile = builder._apply_fallback("hybrid")
    
    section_ids = [s.id for s in profile.expansion_sections]
    expected = [
        "PROPOSTA_VALOR", "PUBLICO_CANAIS", "MODELO_RECEITA", 
        "ARQUITETURA_TECNICA", "DADOS_INGESTAO", "SEGURANCA_PRIVACIDADE",
        "RISCOS_BARREIRAS", "PREMISSAS_CRESCIMENTO"
    ]
    for e in expected:
        assert e in section_ids
    assert len(section_ids) == 8
