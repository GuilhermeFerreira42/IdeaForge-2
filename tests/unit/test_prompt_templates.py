import pytest
import re
from src.core import prompt_templates

def test_all_templates_exist():
    """Verifica se todos os templates básicos existem e não são vazios."""
    templates = [
        prompt_templates.EXPANSION_SYSTEM_PROMPT,
        prompt_templates.DEFENSE_SYSTEM_PROMPT,
        prompt_templates.CRITIQUE_SYSTEM_PROMPT,
        prompt_templates.SPECIALIST_BASE_PROMPT,
        prompt_templates.ISSUE_TABLE_HEADER,
        prompt_templates.ANTI_PROLIXITY_DEBATE,
        prompt_templates.STYLE_CONTRACT_DEBATE
    ]
    for t in templates:
        assert isinstance(t, str)
        assert len(t) > 0

def test_no_prd_references():
    """Garante que nenhum template contém a palavra 'PRD'."""
    templates = [
        prompt_templates.EXPANSION_SYSTEM_PROMPT,
        prompt_templates.DEFENSE_SYSTEM_PROMPT,
        prompt_templates.CRITIQUE_SYSTEM_PROMPT,
        prompt_templates.SPECIALIST_BASE_PROMPT,
        prompt_templates.ISSUE_TABLE_HEADER,
    ]
    for t in templates:
        assert "PRD" not in t.upper()

def test_placeholders_syntax():
    """Verifica se os placeholders seguem o padrão {{NOME}}."""
    # Coletar todos os placeholders em todos os templates
    all_content = "".join([
        prompt_templates.EXPANSION_SYSTEM_PROMPT,
        prompt_templates.DEFENSE_SYSTEM_PROMPT,
        prompt_templates.CRITIQUE_SYSTEM_PROMPT,
        prompt_templates.SPECIALIST_BASE_PROMPT
    ])
    
    # Encontrar qualquer coisa que pareça um placeholder { ... }
    # Padrão correto: {{TEXTO}}
    # Padrões suspeitos: {TEXTO} (único) ou {{{TEXTO}}} (triplo)
    
    matches = re.findall(r'\{+.*?\}+', all_content)
    # Filtrar matches vazios ou que não são placeholders
    for m in matches:
        if m == "{}": continue
        assert m.startswith("{{") and m.endswith("}}"), f"Placeholder malformado: {m}"
        assert not m.startswith("{{{"), f"Placeholder com chaves demais: {m}"

def test_issue_table_header_has_4_columns():
    """Verifica se o header da tabela de issues tem exatamente 4 colunas e não tem ID."""
    header = prompt_templates.ISSUE_TABLE_HEADER
    # Procura a linha de colunas: | Severidade | Categoria | Descrição | Sugestão |
    # Deve ter 5 pipes para 4 colunas
    lines = header.split('\n')
    table_line = [l for l in lines if '|' in l][0]
    columns = [c.strip() for c in table_line.split('|') if c.strip()]
    
    assert len(columns) == 4
    assert "ID" not in [c.upper() for c in columns]
    assert columns[0].lower() in ["severidade", "severity"]
    # Alguma coluna deve ser 'Categoria'
    assert any(c.lower() in ["categoria", "category"] for c in columns)

def test_no_id_column_in_critic_prompt():
    """Garante que o prompt do Critic não pede uma coluna de ID na tabela."""
    prompt = prompt_templates.CRITIQUE_SYSTEM_PROMPT
    # Verifica se o header da tabela no prompt não tem ID
    assert "| ID |" not in prompt
    assert "| ID|" not in prompt
    assert "|ID |" not in prompt
    # Garante que há instrução de NÃO gerar ID
    assert "NÃO gerar ID" in prompt or "atribui IDs automaticamente" in prompt

def test_canonicalization_map_exists_and_is_complete():
    """Verifica se o mapa de normalização PT->EN está presente e completo."""
    mapping = prompt_templates.PT_EN_NORMALIZATION_MAP
    expected_keys = [
        "MEDIUM", "MÉDIA", "MODERADO",
        "CRITICAL", "CRÍTICO", "GRAVE",
        "MINOR", "MENOR", "BAIXO",
        "SEGURANÇA",
        "CORREÇÃO", "CORRETUDE",
        "COMPLETUDE",
        "CONSISTÊNCIA",
        "VIABILIDADE",
        "ESCALABILIDADE"
    ]
    for key in expected_keys:
        assert key.upper() in [k.upper() for k in mapping.keys()]
