import numpy as np
import pandas as pd


METRIC_COLS = [
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
]


def print_dataframe(scores):
    print("\n=== DATAFRAME ===")
    display_df = scores.copy()
    for col in METRIC_COLS:
        if col in display_df.columns:
            display_df[col] = display_df[col].apply(
                lambda x: "TIMEOUT" if pd.isna(x) else round(float(x), 4)
            )
    print(display_df)


def print_diagnostics(scores):
    print("\n=== DIAGNOSTICO DETALLADO ===")
    for idx, row in scores.iterrows():
        print("\n" + "=" * 100)
        print(f"QUERY #{idx + 1}")
        print("\nQUESTION:")
        print(row.get("user_input"))
        print("\nANSWER:")
        print(row.get("response"))
        print("\nMETRICAS:")
        for col in METRIC_COLS:
            if col in row:
                val = "TIMEOUT" if pd.isna(row[col]) else round(float(row[col]), 4)
                print(f"  {col}: {val}")
        print("\nCONTEXTS:")
        contexts = row.get("retrieved_contexts")
        if isinstance(contexts, list):
            for n, ctx in enumerate(contexts, start=1):
                print(f"\n[{n}]")
                if ctx:
                    print(str(ctx)[:800])
        else:
            print(contexts)
        print("\n" + "=" * 100)


def print_performance(rows):
    print("\n=== PERFORMANCE DEL PIPELINE ===")
    for idx, row in enumerate(rows, start=1):
        t = row["timings"]
        print(
            f"Query #{idx}: "
            f"ingest={t['ingest']:.3f}s | "
            f"classify={t['classify']:.3f}s | "
            f"explain={t['explain']:.3f}s | "
            f"total={t['pipeline']:.3f}s"
        )


def print_gate(faith, coverage, min_faith, min_cov):
    print("\n=== GATE P5 ===")
    if coverage < min_cov:
        print(f"❌ FAIL - Cobertura insuficiente ({coverage:.1%})")
    elif faith >= min_faith:
        print(f"✅ PASS - Faithfulness = {faith:.4f}")
    else:
        print(f"❌ FAIL - Faithfulness = {faith:.4f}")
        print(f"Objetivo requerido: {min_faith:.2f}")
        print(f"Diferencia: {(min_faith - faith):.4f}")


def print_summary(rows, scores, faith, coverage, eval_seconds,
                  min_faith, min_cov):
    avg_pipeline = np.mean([r["timings"]["pipeline"] for r in rows])
    avg_explain = np.mean([r["timings"]["explain"] for r in rows])
    total = len(scores)

    timeout_rows = scores[scores["faithfulness"].isna()]
    failed_rows = scores[
        scores["faithfulness"].notna() & (scores["faithfulness"] < min_faith)
    ]

    print("\n=== RESUMEN METRICAS RAGAS ===")
    for col in METRIC_COLS:
        if col in scores.columns:
            valid = scores[col].notna().sum()
            col_cov = valid / total if total > 0 else 0.0
            col_mean = float(np.nanmean(scores[col])) if valid > 0 else 0.0
            print(f"{col:<20} {col_mean:.4f}  (cobertura: {col_cov:.1%} | {valid}/{total})")

    print("\n=== VALIDACION GATE P5 ===")
    print(
        "✅ Cobertura suficiente" if coverage >= min_cov
        else "❌ Cobertura insuficiente"
    )
    print(
        "✅ Faithfulness objetivo alcanzado" if faith >= min_faith
        else "❌ Faithfulness por debajo del objetivo"
    )

    if len(timeout_rows) > 0:
        print(f"\nQueries con TIMEOUT (faithfulness): {len(timeout_rows)}")
        for idx in timeout_rows.index:
            print(f"- Query #{idx + 1} (TIMEOUT)")

    print(f"\nQueries problemáticas (faithfulness < {min_faith:.2f}): {len(failed_rows)}")
    for idx in failed_rows.index:
        print(f"- Query #{idx + 1} (score={scores.loc[idx, 'faithfulness']:.4f})")

    print("\n=== PERFORMANCE GLOBAL ===")
    print(f"Pipeline medio:     {avg_pipeline:.2f}s")
    print(f"RAG+LLM medio:      {avg_explain:.2f}s")
    print(f"Evaluacion RAGAS:   {eval_seconds:.2f}s")
    print(f"\nScore Final P5:     {faith:.4f}")