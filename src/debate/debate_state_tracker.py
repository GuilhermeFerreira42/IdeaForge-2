import re
import unicodedata
from typing import List, Set
from src.core.validation_board import (
    ValidationBoard,
    IssueRecord,
    DecisionRecord,
    AssumptionRecord
)

STOPWORDS_PT: Set[str] = {
    "o", "a", "de", "que", "para", "com", "em", "é", "um", "uma",
    "os", "as", "do", "da", "dos", "das", "no", "na", "nos", "nas",
    "se", "ao", "por", "mais", "não", "como", "mas", "ou", "este",
    "essa", "esse", "isso", "ser", "ter", "foi", "são", "está"
}

KEYWORDS_CATEGORY = {
    "SECURITY": ["segurança", "vulnerabilidade", "autenticação", "exposição", "credencial", "security", "auth", "exposed"],
    "CORRECTNESS": ["erro", "incorreto", "bug", "contradição", "falso", "errado", "error", "incorrect", "wrong", "contradiction"],
    "COMPLETENESS": ["falta", "ausente", "incompleto", "lacuna", "indefinido", "missing", "incomplete", "gap", "undefined"],
    "CONSISTENCY": ["inconsistente", "conflito", "diverge", "contradiz", "inconsistent", "conflict", "diverges"],
    "FEASIBILITY": ["inviável", "irrealista", "impossível", "custo", "infeasible", "unrealistic", "impossible"],
    "SCALABILITY": ["escala", "gargalo", "bottleneck", "performance", "throughput", "scale", "bottleneck"]
}

KEYWORDS_SEVERITY = {
    "HIGH": ["crític", "grave", "bloqueante", "sério", "urgente", "critical", "blocking", "severe", "urgent"],
    "MED": ["importante", "relevante", "moderado", "significativo", "important", "moderate", "significant"],
    "LOW": ["menor", "cosmético", "sugestão", "trivial", "opcional", "minor", "cosmetic", "suggestion", "trivial"]
}

class DebateStateTracker:
    
    def _normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        text = re.sub(r'[^\w\s]', '', text)      # remove pontuação
        text = re.sub(r'\s+', ' ', text)          # colapsa espaços
        words = text.split()
        words = [w for w in words if w not in STOPWORDS_PT]
        return ' '.join(words)[:40] # Prefixo de 40 chars
    
    def _parse_level1(self, text: str, round_num: int) -> List[IssueRecord]:
        records = []
        pattern = r'\|\s*(ISS-\d+)\s*\|\s*(HIGH|MED|LOW)\s*\|\s*(\w+)\s*\|\s*([^|]+)\|'
        for match in re.finditer(pattern, text):
            issue_id = match.group(1).strip()
            severity = match.group(2).strip()
            category = match.group(3).strip()
            description = match.group(4).strip()
            records.append(IssueRecord(issue_id, severity, category, description, round_raised=round_num))
        return records

    def _parse_level2(self, text: str, round_num: int) -> List[IssueRecord]:
        records = []
        # - [HIGH] Description
        pattern1 = r'-\s*\[(HIGH|MED|LOW)\]\s*(.+?)(?:\r?\n|$)'
        # - HIGH: Description
        pattern2 = r'-\s*(HIGH|MED|LOW)\s*[:\-]\s*(.+?)(?:\r?\n|$)'
        
        for p in [pattern1, pattern2]:
            for match in re.finditer(p, text):
                severity = match.group(1).strip()
                description = match.group(2).strip()
                # Auto id and category
                issue_id = f"ISS-{hash(description) % 10000:04d}"
                records.append(IssueRecord(issue_id, severity, "COMPLETENESS", description, round_raised=round_num))
        return records

    def _parse_level3(self, text: str, round_num: int) -> List[IssueRecord]:
        records = []
        sentences = re.split(r'\.\s+|\n', text)
        for sentence in sentences:
            normalized = sentence.lower()
            
            found_sev = None
            for sev, kws in KEYWORDS_SEVERITY.items():
                if any(kw in normalized for kw in kws):
                    found_sev = sev
                    break
                    
            found_cat = None
            for cat, kws in KEYWORDS_CATEGORY.items():
                if any(kw in normalized for kw in kws):
                    found_cat = cat
                    break
            
            if found_sev and found_cat:
                issue_id = f"ISS-{hash(sentence) % 10000:04d}"
                records.append(IssueRecord(issue_id, found_sev, found_cat, sentence.strip()[:200], round_raised=round_num))
                
        return records

    def _deduplicate(self, records: List[IssueRecord], board: ValidationBoard) -> List[IssueRecord]:
        unique_records = []
        existing_normalized = [self._normalize_text(i.description) for i in board._issues.values()]
        
        for r in records:
            norm = self._normalize_text(r.description)
            if norm not in existing_normalized and r.issue_id not in board._issues:
                unique_records.append(r)
                existing_normalized.append(norm)
        return unique_records

    def extract_issues_from_critique(self, critique_text: str, round_num: int, board: ValidationBoard) -> List[str]:
        records = self._parse_level1(critique_text, round_num)
        if not records:
            records = self._parse_level2(critique_text, round_num)
            if not records:
                records = self._parse_level3(critique_text, round_num)
                
        records = self._deduplicate(records, board)
        
        ids = []
        for r in records:
            board.add_issue(r)
            ids.append(r.issue_id)
        return ids

    def extract_resolutions_from_defense(self, defense_text: str, round_num: int, board: ValidationBoard) -> List[str]:
        resolved_ids = []
        # Find block of accepted points
        if "Pontos Aceitos" in defense_text or "resoluções" in defense_text.lower():
            for issue_id, issue in board._issues.items():
                if issue.status == "OPEN" and issue_id in defense_text:
                    try:
                        board.resolve_issue(issue_id, round_num, "Accepted based on defense text")
                        resolved_ids.append(issue_id)
                    except:
                        pass
        return resolved_ids

    def extract_decisions_from_text(self, text: str, round_num: int, board: ValidationBoard) -> List[str]:
        records = []
        pattern = r'-\s*(D-\d+):\s*(.+?)(?:\r?\n|$)'
        for match in re.finditer(pattern, text):
            decision_id = match.group(1).strip()
            description = match.group(2).strip()
            records.append(DecisionRecord(decision_id, description, round_raised=round_num))
            
        ids = []
        for r in records:
            board.add_decision(r)
            ids.append(r.decision_id)
        return ids

    def register_assumptions_from_text(self, text: str, round_num: int, board: ValidationBoard) -> None:
        if "Pressupostos" in text or "assumptions" in text.lower():
            # Very simplistic extraction of numbered items or bullets after Pressupostos
            block = text.split("Pressupostos:")[1] if "Pressupostos:" in text else text
            pattern = r'(?:\d+\.|\-)\s*(.+?)(?:\r?\n|$)'
            for match in re.finditer(pattern, block):
                desc = match.group(1).strip()
                if desc and len(desc) > 5:
                    a_id = f"P-{hash(desc) % 10000:04d}"
                    board.add_assumption(AssumptionRecord(a_id, desc, round_raised=round_num))
