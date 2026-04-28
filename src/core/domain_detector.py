from dataclasses import dataclass
from typing import Optional, List
import re

DOMAIN_KEYWORDS = {
    "software": [
        "api", "banco de dados", "backend", "frontend", "microservices",
        "kubernetes", "docker", "cloud", "aws", "arquitetura",
        "scalability", "performance", "latency", "throughput", "autenticação", "segurança",
        "machine learning", "serverless", "ia", "agente", "automatiz", "infraestrutura"
    ],
    "business": [
        "mercado", "cliente", "receita", "custo", "margem",
        "unit economics", "ltv", "cac", "churn", "growth",
        "competição", "positioning", "go-to-market", "saas", "modelo de negócio",
        "lucro", "afiliado", "seo", "conversão", "marketing", "plataforma", "venda"
    ],
    # ... outros domínios permanecem iguais ...
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
    Implementa normalização por densidade (W5Q-02).
    """
    
    def __init__(self, keywords_map: Optional[dict] = None):
        self.keywords_map = keywords_map or DOMAIN_KEYWORDS
    
    def detect(self, idea: str) -> DomainDetectionResult:
        """
        Detecta domínio analisando densidade de keywords (W5Q-02).
        """
        normalized_idea = idea.lower()
        
        matches = {}
        densities = {}
        
        for domain, keywords in self.keywords_map.items():
            domain_matches = []
            for kw in keywords:
                if kw in normalized_idea:
                    domain_matches.append(kw)
            
            if domain_matches:
                unique_matches = len(set(domain_matches))
                total_domain_keywords = len(keywords)
                # Densidade = matches únicos / total de keywords do domínio
                densities[domain] = unique_matches / total_domain_keywords
                matches[domain] = domain_matches
        
        if not densities:
            return DomainDetectionResult(domain="generic", confidence=0.0, matched_keywords=[])
        
        # Encontrar os dois melhores para checar hybrid (software e business)
        best_domain = max(densities, key=densities.get)
        
        # Lógica especial para HYBRID (W5Q-02)
        # Se software e business empatarem na densidade, retorna hybrid
        if "software" in densities and "business" in densities:
            soft_dense = densities["software"]
            bus_dense = densities["business"]
            
            # Margem de tolerância para empate: 0.01
            if abs(soft_dense - bus_dense) < 0.01:
                return DomainDetectionResult(
                    domain="hybrid",
                    confidence=max(soft_dense, bus_dense) * 5.0, # Normalizar confiança
                    matched_keywords=list(set(matches["software"] + matches["business"]))
                )

        max_density = densities[best_domain]
        confidence = min(1.0, max_density * 5.0) # Heurística: 20% das keywords = 100% conf
        
        return DomainDetectionResult(
            domain=best_domain,
            confidence=confidence,
            matched_keywords=matches[best_domain]
        )
