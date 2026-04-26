from dataclasses import dataclass
from typing import Optional, List
import re

DOMAIN_KEYWORDS = {
    "software": [
        "api", "banco de dados", "backend", "frontend", "microservices",
        "kubernetes", "docker", "cloud", "aws", "arquitetura",
        "scalability", "performance", "latency", "throughput", "autenticação", "segurança"
    ],
    "business": [
        "mercado", "cliente", "receita", "custo", "margem",
        "unit economics", "ltv", "cac", "churn", "growth",
        "competição", "positioning", "go-to-market", "saas", "modelo de negócio"
    ],
    "event": [
        "evento", "conferência", "workshop", "hackathon",
        "logística", "venue", "catering", "transporte",
        "orçamento", "cronograma"
    ],
    "philosophy": [
        "tese", "conceito", "lógica", "ética", "epistemologia",
        "argumento", "premissa", "conclusão", "validade",
        "ontologia", "fenômeno", "kantiana"
    ],
    "research": [
        "pesquisa", "estudo", "hipótese", "metodologia",
        "experimento", "dado", "resultado", "publicação",
        "peer-review", "literatura"
    ],
    "education": [
        "currículo", "pedagogia", "aprendizado", "aluno",
        "didática", "educação", "ensino", "formação",
        "competência", "objetivo pedagógico"
    ]
}

@dataclass
class DomainDetectionResult:
    domain: str                  # "software" | "business" | ... | "generic"
    confidence: float            # 0.0 a 1.0
    matched_keywords: List[str]  # keywords encontradas
    
    def is_confident(self, threshold: float = 0.5) -> bool:
        return self.confidence >= threshold

class DomainDetector:
    """
    Classificador de domínio 100% programático.
    Sem LLM, sem I/O, sem estado — apenas keywords e heurística.
    """
    
    def __init__(self, keywords_map: Optional[dict] = None):
        self.keywords_map = keywords_map or DOMAIN_KEYWORDS
    
    def detect(self, idea: str) -> DomainDetectionResult:
        """
        Detecta domínio analisando keywords na ideia.
        """
        normalized_idea = idea.lower()
        
        scores = {}
        matches = {}
        
        for domain, keywords in self.keywords_map.items():
            domain_matches = []
            for kw in keywords:
                if kw in normalized_idea:
                    domain_matches.append(kw)
            
            if domain_matches:
                # Score simples: número de matches únicos
                scores[domain] = len(set(domain_matches))
                matches[domain] = domain_matches
        
        if not scores:
            return DomainDetectionResult(domain="generic", confidence=0.0, matched_keywords=[])
        
        # Encontrar o domínio com maior score
        best_domain = max(scores, key=scores.get)
        max_score = scores[best_domain]
        
        # Confidence baseada na densidade de matches (heurística simples)
        # Se max_score >= 2, confiança alta. Se 1, média.
        confidence = min(1.0, max_score * 0.4)
        
        if confidence < 0.5:
             # Se confiança muito baixa, ainda pode ser generic se quisermos rigor
             # Mas o detector deve retornar o que achou se o contrato pedir
             pass

        return DomainDetectionResult(
            domain=best_domain,
            confidence=confidence,
            matched_keywords=matches[best_domain]
        )
