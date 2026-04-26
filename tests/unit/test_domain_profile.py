import pytest
from src.core.domain_profile import DomainProfile, ExpansionSection, ValidationDimension

def test_create_profile():
    profile = DomainProfile(
        domain="test",
        confidence=1.0,
        source="manual",
        expansion_sections=[ExpansionSection(id="S1", title="Section 1", instruction="Do X")],
        validation_dimensions=[ValidationDimension(id="D1", display_name="Dim 1", description="Valid X", spawn_hint="Expert")],
        report_sections=[]
    )
    assert profile.domain == "test"
    assert profile.get_section_by_id("S1").title == "Section 1"
    assert profile.get_dimension_by_id("D1").display_name == "Dim 1"
    assert "D1" in profile.get_dimension_ids()

def test_get_invalid_ids():
    profile = DomainProfile("test", 1.0, "manual", [], [], [])
    assert profile.get_section_by_id("INVALID") is None
    assert profile.get_dimension_by_id("INVALID") is None
