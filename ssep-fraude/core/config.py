import os
from dataclasses import dataclass
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

@dataclass(frozen=True)
class SynthConfig:
    provider: str        # "ollama" | "openai"
    model: str
    ollama_url: str
    openai_key: str
    openai_base: str


@dataclass(frozen=True)
class JudgeConfig:
    provider: str        # "ollama" | "openai"
    model: str
    ollama_url: str
    openai_key: str
    openai_base: str
    seed: int
    num_predict: int


@dataclass(frozen=True)
class JudgeEmbeddingsConfig:
    provider: str        # "huggingface" | "openai"
    model: str
    openai_key: str


@dataclass(frozen=True)
class AppConfig:
    synth: SynthConfig
    judge: JudgeConfig
    judge_embeddings: JudgeEmbeddingsConfig


def load_config() -> AppConfig:
    """Lee .env y devuelve config inmutable. Defaults = estado actual."""
    return AppConfig(
        synth=SynthConfig(
            provider=os.getenv("SYNTH_PROVIDER", "ollama"),
            model=os.getenv("SYNTH_MODEL", "llama3.2:3b"),
            ollama_url=os.getenv("SYNTH_OLLAMA_URL", "http://127.0.0.1:11434"),
            openai_key=os.getenv("SYNTH_OPENAI_KEY", ""),
            openai_base=os.getenv("SYNTH_OPENAI_BASE", "https://api.openai.com/v1"),
        ),
        judge=JudgeConfig(
            provider=os.getenv("JUDGE_PROVIDER", "ollama"),
            model=os.getenv("JUDGE_MODEL", "qwen2.5:3b"),
            ollama_url=os.getenv("JUDGE_OLLAMA_URL", "http://127.0.0.1:11434"),
            openai_key=os.getenv("JUDGE_OPENAI_KEY", ""),
            openai_base=os.getenv("JUDGE_OPENAI_BASE", "https://api.openai.com/v1"),
            seed=int(os.getenv("JUDGE_SEED", "42")),
            num_predict=int(os.getenv("JUDGE_NUM_PREDICT", "1024")),
        ),
        judge_embeddings=JudgeEmbeddingsConfig(
            provider=os.getenv("JUDGE_EMB_PROVIDER", "huggingface"),
            model=os.getenv(
                "JUDGE_EMB_MODEL",
                "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            ),
            openai_key=os.getenv("JUDGE_EMB_OPENAI_KEY", os.getenv("JUDGE_OPENAI_KEY", "")),
        ),
    )