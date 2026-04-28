import pytest
from src.core.domain_detector import DomainDetector, DomainDetectionResult

def test_detect_software_domain():
    detector = DomainDetector()
    result = detector.detect("Precisamos de uma arquitetura backend escalável com Kubernetes")
    assert result.domain == "software"
    assert "backend" in result.matched_keywords or "arquitetura" in result.matched_keywords
    assert result.confidence > 0.5

def test_detect_business_domain():
    detector = DomainDetector()
    result = detector.detect("Qual o unit economics e go-to-market deste SaaS?")
    assert result.domain == "business"
    assert "unit economics" in result.matched_keywords or "go-to-market" in result.matched_keywords

def test_detect_philosophy_domain():
    detector = DomainDetector()
    result = detector.detect("Uma tese sobre ética e epistemologia kantiana")
    assert result.domain == "philosophy"

def test_fallback_to_generic():
    detector = DomainDetector()
    result = detector.detect("Uma ideia qualquer sem keywords específicas")
    assert result.domain in ["generic", "software"]
    assert result.confidence < 0.5

def test_performance_under_100ms():
    import time
    detector = DomainDetector()
    start = time.time()
    detector.detect("Teste de performance")
    end = time.time()
    assert (end - start) < 0.1

def test_detect_hybrid_quando_software_e_business_empatam():
    """W5Q-02: Se software e business têm a mesma densidade, retorna hybrid."""
    detector = DomainDetector()
    # 1 keyword business ("mercado"), 1 keyword software ("api")
    result = detector.detect("Uma api para o mercado de varejo")
    assert result.domain == "hybrid"

def test_detect_business_mesmo_com_keyword_software_isolada():
    """W5Q-02: Ideia de negócio com 1 termo técnico deve ser business (via densidade)."""
    detector = DomainDetector()
    # 3 keywords business (lucro, mercado, cliente), 1 software (api)
    # Obs: lucro e cliente precisam estar na lista business expandida
    result = detector.detect("Aumentar o lucro no mercado atraindo cada cliente via api")
    assert result.domain == "business"

def test_detect_software_mesmo_com_keyword_business_isolada():
    """W5Q-02: Ideia técnica com 1 termo de negócio deve ser software (via densidade)."""
    detector = DomainDetector()
    # 3 keywords software (kubernetes, docker, cloud), 1 business (saas)
    result = detector.detect("Setup de kubernetes e docker na cloud para meu saas")
    assert result.domain == "software"
