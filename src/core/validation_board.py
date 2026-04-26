import json
import os
import hashlib
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from src.core.domain_profile import DomainProfile

class InvalidStateTransitionError(Exception):
    def __init__(self, record_id: str, current: str, attempted: str):
        self.record_id = record_id
        self.current = current
        self.attempted = attempted
        super().__init__(
            f"[{record_id}] Transição inválida: '{attempted}' a partir do estado '{current}'"
        )

@dataclass
class IssueRecord:
    issue_id: str
    severity: str
    category: str
    description: str
    status: str = "OPEN"
    round_raised: int = 0
    round_resolved: Optional[int] = None
    resolution: str = ""

@dataclass
class DecisionRecord:
    decision_id: str
    description: str
    status: str = "PROPOSED"
    round_raised: int = 0
    round_resolved: Optional[int] = None
    evidence: str = ""

@dataclass
class AssumptionRecord:
    assumption_id: str
    description: str
    status: str = "UNTESTED"
    round_raised: int = 0
    round_resolved: Optional[int] = None
    evidence: str = ""

class ValidationBoard:
    def __init__(self, profile: Optional[DomainProfile] = None):
        self._issues: Dict[str, IssueRecord] = {}
        self._decisions: Dict[str, DecisionRecord] = {}
        self._assumptions: Dict[str, AssumptionRecord] = {}
        self._profile = profile
        self._validation_schema: Dict[str, Any] = {}
        
        self._meta: Dict[str, Any] = {
            "version": "1.1",
            "created_at": datetime.now().isoformat(),
            "next_ids": {"issue": 1, "decision": 1, "assumption": 1}
        }
        
        if profile:
            self.set_domain_profile(profile)
        
        # Ensure dir exists
        os.makedirs(".forge", exist_ok=True)

    def set_domain_profile(self, profile: DomainProfile) -> None:
        """Injeta DomainProfile dinâmico no board."""
        self._profile = profile
        self._validation_schema = {
            dim.id: {
                "display_name": dim.display_name,
                "description": dim.description,
                "spawn_hint": dim.spawn_hint
            }
            for dim in profile.validation_dimensions
        }

    def get_domain_profile(self) -> Optional[DomainProfile]:
        return self._profile

    def is_valid_category(self, category: str) -> bool:
        """Verifica se categoria é válida no schema dinâmico."""
        if not self._validation_schema:
            return True # Retrocompatibilidade: se sem profile, aceita tudo
        return category.upper() in self._validation_schema

    def get_open_issues_by_category(self) -> Dict[str, List[IssueRecord]]:
        """Agrupa issues abertos por categoria."""
        by_category = {}
        for issue in self._issues.values():
            if issue.status == "OPEN":
                cat = issue.category.upper()
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(issue)
        return by_category

    def get_dominant_open_category(self) -> Optional[str]:
        """Retorna categoria com mais issues abertos."""
        by_cat = self.get_open_issues_by_category()
        if not by_cat:
            return None
        return max(by_cat.keys(), key=lambda k: len(by_cat[k]))

    def add_issue(self, record: IssueRecord) -> None:
        if record.issue_id in self._issues:
            return
        self._issues[record.issue_id] = record
        
    def get_issue(self, issue_id: str) -> Optional[IssueRecord]:
        """Retorna um registro de issue pelo ID."""
        return self._issues.get(issue_id)
        
    def resolve_issue(self, issue_id: str, round_num: int, resolution: str) -> None:
        issue = self._issues[issue_id]
        if issue.status != "OPEN":
            raise InvalidStateTransitionError(issue_id, issue.status, "resolve_issue")
        if resolution:
            issue.status = "RESOLVED"
            issue.round_resolved = round_num
            issue.resolution = resolution

    def defer_issue(self, issue_id: str, round_num: int) -> None:
        issue = self._issues[issue_id]
        if issue.status != "OPEN":
            raise InvalidStateTransitionError(issue_id, issue.status, "defer_issue")
        issue.status = "DEFERRED"
        issue.round_resolved = round_num

    def add_decision(self, record: DecisionRecord) -> None:
        if record.decision_id in self._decisions:
            return
        self._decisions[record.decision_id] = record

    def validate_decision(self, decision_id: str, round_num: int, evidence: str) -> None:
        decision = self._decisions[decision_id]
        if decision.status != "PROPOSED":
            raise InvalidStateTransitionError(decision_id, decision.status, "validate_decision")
        if evidence:
            decision.status = "VALIDATED"
            decision.round_resolved = round_num
            decision.evidence = evidence

    def contest_decision(self, decision_id: str, round_num: int) -> None:
        decision = self._decisions[decision_id]
        if decision.status != "PROPOSED":
            raise InvalidStateTransitionError(decision_id, decision.status, "contest_decision")
        decision.status = "CONTESTED"
        decision.round_resolved = round_num

    def add_assumption(self, record: AssumptionRecord) -> None:
        if record.assumption_id in self._assumptions:
            return
        self._assumptions[record.assumption_id] = record

    def validate_assumption(self, assumption_id: str, round_num: int, evidence: str) -> None:
        assumption = self._assumptions[assumption_id]
        if assumption.status != "UNTESTED":
            raise InvalidStateTransitionError(assumption_id, assumption.status, "validate_assumption")
        if evidence:
            assumption.status = "VALIDATED"
            assumption.round_resolved = round_num
            assumption.evidence = evidence

    def flag_assumption(self, assumption_id: str, round_num: int) -> None:
        assumption = self._assumptions[assumption_id]
        if assumption.status != "UNTESTED":
            raise InvalidStateTransitionError(assumption_id, assumption.status, "flag_assumption")
        assumption.status = "FLAGGED"
        assumption.round_resolved = round_num

    def get_open_issues(self) -> List[IssueRecord]:
        issues = [i for i in self._issues.values() if i.status == "OPEN"]
        # Order HIGH -> MED -> LOW
        order = {"HIGH": 0, "MED": 1, "LOW": 2}
        return sorted(issues, key=lambda x: order.get(x.severity, 3))

    def get_validated_decisions(self) -> List[DecisionRecord]:
        return [d for d in self._decisions.values() if d.status == "VALIDATED"]

    def get_untested_assumptions(self) -> List[AssumptionRecord]:
        return [a for a in self._assumptions.values() if a.status == "UNTESTED"]

    def has_blocking_issues(self) -> bool:
        return any(i.severity == "HIGH" for i in self.get_open_issues())

    def get_stats(self) -> Dict[str, int]:
        return {
            "total_issues": len(self._issues),
            "open_issues": len(self.get_open_issues()),
            "total_decisions": len(self._decisions),
            "validated_decisions": len(self.get_validated_decisions()),
            "total_assumptions": len(self._assumptions),
            "untested_assumptions": len(self.get_untested_assumptions())
        }

    def get_issues_for_proponent_prompt(self) -> str:
        open_issues = self.get_open_issues()
        if not open_issues:
            return "Nenhum issue aberto."
        lines = ["DEVE ENDEREÇAR:"]
        for i in open_issues:
            lines.append(f"- {i.issue_id} [{i.severity}]: {i.description}")
        return "\n".join(lines)

    def get_open_issues_for_critic_prompt(self) -> str:
        return self.get_issues_for_proponent_prompt()

    def get_validated_decisions_prompt(self) -> str:
        decisions = self.get_validated_decisions()
        if not decisions:
            return "Nenhuma decisão consolidada."
        lines = ["DECISÕES VALIDADAS:"]
        for d in decisions:
            lines.append(f"- {d.decision_id}: {d.description}")
        return "\n".join(lines)

    def get_consolidation_summary(self) -> str:
        # Max ~2500 chars limit by blueprint
        summary = "## Sumário de Validação\n\n"
        summary += self.get_validated_decisions_prompt() + "\n\n"
        summary += self.get_issues_for_proponent_prompt()
        return summary[:2500]

    def snapshot(self) -> Dict[str, Any]:
        data = {
            "_meta": self._meta.copy(),
            "issues": {k: asdict(v) for k, v in self._issues.items()},
            "decisions": {k: asdict(v) for k, v in self._decisions.items()},
            "assumptions": {k: asdict(v) for k, v in self._assumptions.items()}
        }
        json_str = json.dumps(data, sort_keys=True)
        data["_meta"]["fingerprint"] = hashlib.sha256(json_str.encode()).hexdigest()
        return data

    def persist(self, path: str = ".forge/validation_board.json") -> None:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.snapshot(), f, indent=2, sort_keys=True)
        except OSError:
            pass # Logging goes here if pipeline_logger was available, but required not to raise

    @classmethod
    def from_snapshot(cls, data: Dict[str, Any]) -> 'ValidationBoard':
        board = cls()
        board._meta = data.get("_meta", board._meta)
        
        for k, v in data.get("issues", {}).items():
            board._issues[k] = IssueRecord(**v)
            
        for k, v in data.get("decisions", {}).items():
            board._decisions[k] = DecisionRecord(**v)
            
        for k, v in data.get("assumptions", {}).items():
            board._assumptions[k] = AssumptionRecord(**v)
            
        return board
