"""Deterministic mock for optional supervisory chat (no live LLM providers)."""
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Ipi Dlbcl Prognostic Index"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return (
            f"[{self.system_name} mock]: Received query: {prompt[:60]}... "
            "No model inference, clinical assessment, or scientific validation was performed."
        )


class LLMFactory:
    """Select deterministic mock; reject provider names without implemented adapters."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Ipi Dlbcl Prognostic Index"):
        if str(provider).lower() in ("mock", "deterministic", "test"):
            return MockLLM(system_name)
        raise ValueError(f"Unsupported model provider: {provider}. Only deterministic mock is available.")
