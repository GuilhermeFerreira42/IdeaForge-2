import pytest
from src.core.domain_profile import DomainProfile, ValidationDimension
from src.core.category_normalizer import CategoryNormalizer

@pytest.fixture
def business_profile():
    return DomainProfile(
        domain="business",
        confidence=1.0,
        source="manual",
        expansion_sections=[],
        validation_dimensions=[
            ValidationDimension(id="MARKET_FIT", display_name="Encaixe de Mercado", description="Desc", spawn_hint="Expert", keywords=["MERCADO", "DEMANDA"]),
            ValidationDimension(id="UNIT_ECONOMICS", display_name="Economia Unitária", description="Desc", spawn_hint="Expert", keywords=["FINANCEIRO", "CUSTO"])
        ],
        report_sections=[]
    )

def test_normalize_valid_id(business_profile):
    normalizer = CategoryNormalizer(business_profile)
    assert normalizer.normalize("MARKET_FIT") == "MARKET_FIT"
    assert normalizer.normalize("market_fit") == "MARKET_FIT"

def test_normalize_via_keywords(business_profile):
    normalizer = CategoryNormalizer(business_profile)
    assert normalizer.normalize("Análise de Mercado") == "MARKET_FIT"
    assert normalizer.normalize("custos operacionais") == "UNIT_ECONOMICS"

def test_normalize_unknown_returns_none(business_profile):
    normalizer = CategoryNormalizer(business_profile)
    assert normalizer.normalize("Culinária") is None
