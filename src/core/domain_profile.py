from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

@dataclass
class ExpansionSection:
    """Define uma seção dinâmica para expansão no Round 0B."""
    id: str                # Ex: "MARKET_ANALYSIS", "LOGICAL_COHERENCE"
    title: str             # Título em PT-BR
    instruction: str       # Instrução curta (max 160 chars)
    max_words: int = 150

@dataclass
class ValidationDimension:
    """Define uma dimensão de validação (categoria) dinâmica."""
    id: str                # Ex: "LOGISTICS", "INTERNAL_CONSISTENCY"
    display_name: str      # Nome para exibição
    description: str       # Descrição curta do que valida
    spawn_hint: str        # Dica de especialista ("Especialista em Logística")
    keywords: List[str] = field(default_factory=list)  # Keywords para detecção

@dataclass
class ReportSection:
    """Define seções do relatório final."""
    id: str
    title: str
    template: str          # Template Markdown com placeholders

@dataclass
class DomainProfile:
    """
    Configuração dinâmica do debate para um domínio específico.
    Produzido pelo DomainContextBuilder no Round 0A.
    Injetado no ValidationBoard antes do Round 0B.
    """
    domain: str                              # "software", "business", etc.
    confidence: float                        # Confiança da detecção (0–1)
    source: str                              # "detector" | "llm" | "fallback"
    
    expansion_sections: List[ExpansionSection]
    validation_dimensions: List[ValidationDimension]
    report_sections: List[ReportSection]
    
    specialist_hints: List[str] = field(default_factory=list)
    critical_questions: List[str] = field(default_factory=list)
    success_criteria: Dict[str, str] = field(default_factory=dict)
    
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_section_by_id(self, section_id: str) -> Optional[ExpansionSection]:
        return next((s for s in self.expansion_sections if s.id == section_id), None)
    
    def get_dimension_by_id(self, dim_id: str) -> Optional[ValidationDimension]:
        return next((d for d in self.validation_dimensions if d.id == dim_id), None)
    
    def get_dimension_ids(self) -> List[str]:
        return [d.id for d in self.validation_dimensions]
