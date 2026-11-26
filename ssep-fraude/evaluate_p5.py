"""P5 — Evaluación RAGAS con juez inyectable (4 métricas completas)."""

import time
import numpy as np
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from ragas.run_config import RunConfig

from core.config import load_config
from core.factories import (
    create_judge_llm,
    create_judge_embeddings,
)

from eval_dataset import EVAL_CASES
from eval_pipeline import run_for_eval
from eval_diagnostics import (
    print_dataframe,
    print_gate,
    print_summary,
)


MIN_COVERAGE = 0.80
MIN_FAITHFULNESS = 0.80


def main():
    cfg = load_config()

    print(f"Synth provider: {cfg.synth.provider} ({cfg.synth.model})")
    print(f"Judge provider: {cfg.judge.provider} ({cfg.judge.model})")
    print(f"Judge emb:      {cfg.judge_embeddings.provider}\n")

    judge_llm = create_judge_llm(cfg)
    judge_embeddings = create_judge_embeddings(cfg)

    print("Ejecutando pipeline...\n")
    rows = []
    for tx_str, card_id, ground_truth in EVAL_CASES:
        print(f"{card_id}...", end=" ")
        row = run_for_eval(tx_str, card_id)
        row["ground_truth"] = ground_truth
        rows.append(row)
        t = row["timings"]
        print(
            f"OK (grounding={row['grounding_score']:.2f}, "
            f"explain={t['explain']:.2f}s, "
            f"total={t['pipeline']:.2f}s)"
        )

    dataset = Dataset.from_list(
        [
            {
                "question": r["question"],
                "answer": r["answer"],
                "contexts": r["contexts"],
                "ground_truth": r["ground_truth"],
            }
            for r in rows
        ]
    )

    print(f"\nEvaluando {len(rows)} queries con RAGAS (4 métricas)...")
    eval_start = time.perf_counter()
    result = evaluate(
        dataset=dataset,
        metrics=[
            faithfulness,
            answer_relevancy,
            context_precision,
            context_recall,
        ],
        llm=judge_llm,
        embeddings=judge_embeddings,
        run_config=RunConfig(max_workers=1, timeout=600, max_retries=2),
    )
    eval_seconds = time.perf_counter() - eval_start

    scores = result.to_pandas()
    print_dataframe(scores)

    evaluated = scores["faithfulness"].notna().sum()
    total = len(scores)
    coverage = evaluated / total if total > 0 else 0.0
    faith = float(np.nanmean(scores["faithfulness"])) if evaluated > 0 else 0.0

    print_gate(faith, coverage, MIN_FAITHFULNESS, MIN_COVERAGE)
    print_summary(
        rows,
        scores,
        faith,
        coverage,
        eval_seconds,
        MIN_FAITHFULNESS,
        MIN_COVERAGE,
    )


if __name__ == "__main__":
    main()