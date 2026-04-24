import pytest
import os
import json
from src.core.validation_board import (
    ValidationBoard,
    IssueRecord,
    DecisionRecord,
    AssumptionRecord,
    InvalidStateTransitionError
)

@pytest.fixture
def empty_board():
    return ValidationBoard()

def test_add_issue_initial_status_open(empty_board):
    record = IssueRecord("ISS-01", "HIGH", "SECURITY", "Test issue")
    empty_board.add_issue(record)
    assert empty_board.get_open_issues()[0].issue_id == "ISS-01"
    assert empty_board._issues["ISS-01"].status == "OPEN"

def test_resolve_issue_transitions_to_resolved(empty_board):
    record = IssueRecord("ISS-01", "HIGH", "SECURITY", "Test issue")
    empty_board.add_issue(record)
    empty_board.resolve_issue("ISS-01", 2, "aceito")
    assert empty_board._issues["ISS-01"].status == "RESOLVED"
    assert empty_board._issues["ISS-01"].round_resolved == 2
    assert empty_board._issues["ISS-01"].resolution == "aceito"

def test_resolve_already_resolved_raises(empty_board):
    record = IssueRecord("ISS-01", "HIGH", "SECURITY", "Test issue")
    empty_board.add_issue(record)
    empty_board.resolve_issue("ISS-01", 2, "aceito")
    with pytest.raises(InvalidStateTransitionError):
        empty_board.resolve_issue("ISS-01", 3, "outro")

def test_add_decision_initial_status_proposed(empty_board):
    record = DecisionRecord("D-01", "Decision 1")
    empty_board.add_decision(record)
    assert "D-01" in empty_board._decisions
    assert empty_board._decisions["D-01"].status == "PROPOSED"

def test_validate_decision_transitions(empty_board):
    record = DecisionRecord("D-01", "Decision 1")
    empty_board.add_decision(record)
    empty_board.validate_decision("D-01", 2, "evidência")
    assert empty_board._decisions["D-01"].status == "VALIDATED"
    assert empty_board._decisions["D-01"].evidence == "evidência"

def test_add_assumption_initial_status_untested(empty_board):
    record = AssumptionRecord("P-01", "Assump")
    empty_board.add_assumption(record)
    assert "P-01" in empty_board._assumptions
    assert empty_board._assumptions["P-01"].status == "UNTESTED"

def test_flag_assumption_transitions(empty_board):
    record = AssumptionRecord("P-01", "Assump")
    empty_board.add_assumption(record)
    empty_board.flag_assumption("P-01", 1)
    assert empty_board._assumptions["P-01"].status == "FLAGGED"

def test_get_open_issues_filters_and_orders(empty_board):
    empty_board.add_issue(IssueRecord("ISS-01", "LOW", "CAT", "Low"))
    empty_board.add_issue(IssueRecord("ISS-02", "HIGH", "CAT", "High"))
    empty_board.add_issue(IssueRecord("ISS-03", "MED", "CAT", "Med"))
    empty_board.add_issue(IssueRecord("ISS-04", "HIGH", "CAT", "Resolved", status="RESOLVED"))

    issues = empty_board.get_open_issues()
    assert len(issues) == 3
    assert all(i.status == "OPEN" for i in issues)
    assert [i.severity for i in issues] == ["HIGH", "MED", "LOW"]

def test_has_blocking_issues_high_open(empty_board):
    assert not empty_board.has_blocking_issues()
    empty_board.add_issue(IssueRecord("ISS-01", "MED", "CAT", "Desc"))
    assert not empty_board.has_blocking_issues()
    empty_board.add_issue(IssueRecord("ISS-02", "HIGH", "CAT", "Desc"))
    assert empty_board.has_blocking_issues()

def test_add_issue_duplicate_id_ignored(empty_board):
    record1 = IssueRecord("ISS-01", "HIGH", "CAT", "Desc 1")
    record2 = IssueRecord("ISS-01", "MED", "CAT", "Desc 2")
    empty_board.add_issue(record1)
    empty_board.add_issue(record2)
    assert len(empty_board._issues) == 1
    assert empty_board._issues["ISS-01"].severity == "HIGH"

def test_snapshot_is_json_serializable(empty_board):
    empty_board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Test"))
    snapshot = empty_board.snapshot()
    json.dumps(snapshot)  # Should not raise
    assert "issues" in snapshot
    assert "ISS-01" in snapshot["issues"]

def test_persist_and_restore_round_trip(empty_board, tmp_path):
    empty_board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Test"))
    empty_board.resolve_issue("ISS-01", 1, "res")
    file_path = str(tmp_path / "board.json")
    empty_board.persist(file_path)
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    restored_board = ValidationBoard.from_snapshot(data)
    assert restored_board.get_stats() == empty_board.get_stats()
    assert restored_board._issues["ISS-01"].status == "RESOLVED"

def test_persist_oserror_no_exception(empty_board):
    empty_board.persist("/root/no_permission.json")  # Should not raise exception
    
def test_consolidation_summary_max_chars(empty_board):
    empty_board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Desc"))
    summary = empty_board.get_consolidation_summary()
    assert isinstance(summary, str)
    assert len(summary) <= 2500

def test_proponent_prompt_contains_open_only(empty_board):
    empty_board.add_issue(IssueRecord("ISS-01", "HIGH", "SECURITY", "Desc 1"))
    empty_board.add_issue(IssueRecord("ISS-02", "HIGH", "SECURITY", "Desc 2", status="RESOLVED"))
    prompt = empty_board.get_issues_for_proponent_prompt()
    assert "DEVE ENDEREÇAR" in prompt
    assert "ISS-01" in prompt
    assert "ISS-02" not in prompt

def test_validated_decisions_prompt_no_proposed(empty_board):
    empty_board.add_decision(DecisionRecord("D-01", "Dec 1"))
    empty_board.add_decision(DecisionRecord("D-02", "Dec 2", status="VALIDATED"))
    prompt = empty_board.get_validated_decisions_prompt()
    assert "D-02" in prompt
    assert "D-01" not in prompt
    assert "PROPOSED" not in prompt
