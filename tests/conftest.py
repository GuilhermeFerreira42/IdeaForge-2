"""
Fixtures compartilhadas para testes do IdeaForge 2.
MockProvider permite testar todo o pipeline sem chamar LLM.
"""
import pytest


class MockProvider:
    """Provider de LLM fake para testes TDD."""

    def __init__(self, responses=None):
        self.responses = responses or {}
        self.call_log = []

    def generate(self, prompt, context=None, role="user", max_tokens=None, think=False):
        self.call_log.append({
            "prompt": prompt[:200],
            "role": role,
            "max_tokens": max_tokens,
        })
        if callable(self.responses):
            return self.responses(prompt)
        return self.responses.get(role, "Mock response for: " + role)


@pytest.fixture
def mock_provider():
    """Fixture que retorna um MockProvider limpo."""
    return MockProvider()


@pytest.fixture
def mock_provider_with_responses():
    """Fixture factory para MockProvider com respostas customizadas."""
    def _factory(responses):
        return MockProvider(responses=responses)
    return _factory
