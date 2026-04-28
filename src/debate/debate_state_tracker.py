import re
import unicodedata
from typing import List, Set
from src.core.validation_board import (
    ValidationBoard,
    IssueRecord,
    DecisionRecord,
    AssumptionRecord
)
from src.core.category_normalizer import CategoryNormalizer
from src.core.convergence_detector import ConvergenceDetector

SEMANTIC_DEDUP_THRESHOLD: float = 0.65

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
    def __init__(self):
        self._convergence_detector = ConvergenceDetector()
    
    def _normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')
        text = re.sub(r'[^\w\s]', '', text)      # remove pontuação
        text = re.sub(r'\s+', ' ', text)          # colapsa espaços
        words = text.split()
        words = [w for w in words if w not in STOPWORDS_PT]
        return ' '.join(words)[:80] # Prefixo de 80 chars (W5Q-03)
    
    def _parse_v4(self, text: str, round_num: int) -> List[IssueRecord]:
        """Extrai issues da tabela Markdown de 4 colunas (Onda 4).
        Formato: | Severidade | Categoria | Descrição | Sugestão |
        """
        records = []
        # Rigor: A severidade deve vir logo após o primeiro pipe da linha (ignora se houver um ID antes)
        pattern = r'^\|\s*(HIGH|MED|LOW)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|\s*([^|]+)\s*\|'
        
        for line in text.split('\n'):
            match = re.match(pattern, line.strip())
            if match:
                severity = match.group(1).strip()
                category_raw = match.group(2).strip()
                description_raw = match.group(3).strip()
                suggestion = match.group(4).strip()
                
                # Pular se for o cabeçalho
                if severity.lower() == "severidade":
                    continue
                
                # Gerar ID único se não presente (sempre ausente na Onda 4 specialists)
                issue_id = f"ISS-{hash(description_raw) % 10000:04d}"
                
                # A descrição incluirá a sugestão para manter o histórico
                description = f"{description_raw} (Sugestão: {suggestion})"
                
                records.append(IssueRecord(
                    issue_id=issue_id,
                    severity=severity,
                    category=category_raw, # Será normalizado depois
                    description=description,
                    round_raised=round_num
                ))
        return records

    def _parse_level1(self, text: str, round_num: int) -> List[IssueRecord]:
        # Mantido para retrocompatibilidade com Tabelas de 3 ou 5 colunas de ondas anteriores
        records = []
        pattern = r'\|\s*(ISS-\d+)\s*\|\s*(HIGH|MED|LOW)\s*\|\s*([\w_]+)\s*\|\s*([^|]+)\|'
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

    def _is_semantic_duplicate(
        self,
        new_description: str,
        board: ValidationBoard,
        category: str,
        threshold: float = SEMANTIC_DEDUP_THRESHOLD
    ) -> bool:
        """
        Verifica se new_description é semanticamente duplicata de algum issue
        já registrado na mesma categoria. (W5Q-03)
        """
        try:
            open_issues = board.get_open_issues()
            same_category = [
                iss for iss in open_issues
                if iss.category.upper() == category.upper()
            ]
            
            new_prefix = self._normalize_text(new_description)
            
            for existing in same_category:
                existing_prefix = self._normalize_text(existing.description)
                similarity = self._convergence_detector.similarity(
                    new_prefix, existing_prefix
                )
                if similarity >= threshold:
                    return True
            
            return False
        except Exception:
            return False

    def _deduplicate(self, records: List[IssueRecord], board: ValidationBoard) -> List[IssueRecord]:
        unique_records = []
        
        for r in records:
            # 1. Dedup por hash de ID (exato)
            if r.issue_id in board._issues:
                continue
                
            # 2. Dedup semântico (W5Q-03)
            if self._is_semantic_duplicate(r.description, board, r.category):
                continue
                
            unique_records.append(r)
        return unique_records

    def extract_issues_from_critique(self, critique_text: str, round_num: int, board: ValidationBoard) -> List[str]:
        # Tenta parse V4 primeiro (Onda 4)
        records = self._parse_v4(critique_text, round_num)
        
        if not records:
            records = self._parse_level1(critique_text, round_num)
            if not records:
                records = self._parse_level2(critique_text, round_num)
                if not records:
                    records = self._parse_level3(critique_text, round_num)
        
        # [ONDA 4] Normalização de Categorias
        normalizer = CategoryNormalizer(board.get_domain_profile())
        for r in records:
            r.category = normalizer.normalize(r.category)
                
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
