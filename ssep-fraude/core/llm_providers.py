from typing import Protocol


class SynthLLM(Protocol):
    """Interfaz mínima que _synthesize necesita."""
    def generate(self, prompt: str) -> str: ...


class OllamaSynthLLM:
    """
    Implementación nativa Ollama.
    Preserva las opciones de Fix C (seed, top_k, top_p) que
    la API OpenAI-compat de Ollama NO expone.
    """

    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url
        self.options = {
            "temperature": 0,
            "seed": 42,
            "top_k": 1,
            "top_p": 0.0,
            "num_predict": 300,
        }

    def generate(self, prompt: str) -> str:
        import ollama
        response = ollama.generate(
            model=self.model,
            prompt=prompt,
            options=self.options,
        )
        return response["response"].strip()


class OpenAISynthLLM:
    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()