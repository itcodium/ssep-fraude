from ragas.llms import LangchainLLMWrapper, llm_factory
from ragas.embeddings import LangchainEmbeddingsWrapper

from .config import AppConfig
from .llm_providers import OllamaSynthLLM, OpenAISynthLLM


def create_synth_llm(cfg: AppConfig):
    if cfg.synth.provider == "ollama":
        return OllamaSynthLLM(cfg.synth.model, cfg.synth.ollama_url)
    if cfg.synth.provider == "openai":
        return OpenAISynthLLM(
            cfg.synth.model, cfg.synth.openai_key, cfg.synth.openai_base
        )
    raise ValueError(f"Unknown SYNTH_PROVIDER: {cfg.synth.provider}")


def create_judge_llm(cfg: AppConfig):
    if cfg.judge.provider == "ollama":
        from langchain_ollama import ChatOllama
        return LangchainLLMWrapper(
            ChatOllama(
                model=cfg.judge.model,
                base_url=cfg.judge.ollama_url,
                temperature=0.0,
                seed=cfg.judge.seed,
                num_predict=cfg.judge.num_predict,
                model_kwargs={"options": {"top_k": 1, "top_p": 0.0}},
            )
        )
    if cfg.judge.provider == "openai":
        from openai import OpenAI
        return llm_factory(
            cfg.judge.model,
            client=OpenAI(
                api_key=cfg.judge.openai_key,
                base_url=cfg.judge.openai_base,
            ),
        )
    raise ValueError(f"Unknown JUDGE_PROVIDER: {cfg.judge.provider}")


def create_judge_embeddings(cfg: AppConfig):
    if cfg.judge_embeddings.provider == "huggingface":
        from langchain_huggingface import HuggingFaceEmbeddings
        return LangchainEmbeddingsWrapper(
            HuggingFaceEmbeddings(model_name=cfg.judge_embeddings.model)
        )
    if cfg.judge_embeddings.provider == "openai":
        from langchain_openai import OpenAIEmbeddings
        return LangchainEmbeddingsWrapper(
            OpenAIEmbeddings(
                model=cfg.judge_embeddings.model,
                api_key=cfg.judge_embeddings.openai_key,
            )
        )
    raise ValueError(
        f"Unknown JUDGE_EMB_PROVIDER: {cfg.judge_embeddings.provider}"
    )