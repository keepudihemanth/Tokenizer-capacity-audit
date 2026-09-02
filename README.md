# Tokenizer & Serving Capacity Audit

## Overview

This project audits:

- **Tokenizer efficiency across English and Indic languages**
- **KV-cache memory capacity**
- **Serving throughput and batch-size behavior**

The work is organized into three parts.

---

## Project Navigation

| Section | Purpose | Key Output |
|---|---|---|
| `PartA/` | Multilingual tokenizer analysis | `benchmark_results.json` |
| `PartB/` | KV-cache and serving analysis | Capacity and throughput findings |
| `PartC/` | Final recommendation | `DECISION_MEMO.md` |
| `bench/` | Benchmark inputs and model specification | `bench_log.csv`, `model_spec.md` |

### Start Here

1. Read **`REPORT.md`** for the final findings.
2. Read **`PartC/DECISION_MEMO.md`** for the final recommendation.
3. Use the scripts in `PartA/` and `PartB/` to reproduce the analysis.

---

# Part A — Tokenizer Analysis

## Goal

Compare tokenization efficiency for:

- English
- Hindi
- Telugu
- Kannada

using:

- GPT-2 tokenizer
- XLM-RoBERTa tokenizer

The evaluation corpus contains **1,012 aligned sentences per language**.

### Main Files

| File | Purpose |
|---|---|
| `prepare_corpus.py` | Prepares the multilingual evaluation corpus |
| `benchmark_tokenizers.py` | Runs the tokenizer benchmark |
| `compare_tokenizers.py` | Compares GPT-2 and XLM-R token counts |
| `benchmark_results.json` | Saved benchmark results |
| `recommendation_memo.md` | Part A findings and recommendation |

### Key Result

Token reduction using XLM-R instead of GPT-2:

| Language | Reduction |
|---|---:|
| English | -13.37% |
| Hindi | 80.93% |
| Telugu | 88.49% |
| Kannada | 88.71% |

The results show that tokenizer choice has a major impact on token usage for the evaluated Indic languages.

---

# Part B — Serving Capacity Analysis

## Goal

Analyze:

- KV-cache memory requirements
- Theoretical concurrent sequence capacity
- Throughput under increasing batch sizes
- KV-cache saturation and preemption

### Main Files

| File | Purpose |
|---|---|
| `calculate_kv_capacity.py` | Calculates theoretical KV-cache capacity |
| `analyze_bench.py` | Analyzes long-context throughput |
| `check_reported_throughput.py` | Verifies what `reported_tok_s` measures |

### Key Results

**Theoretical KV-cache capacity:**

```text
Maximum whole 4096-token sequences = 46
```

**Best measured long-context operating point:**

```text
Batch size          : 24
Generated goodput   : 200.92 tok/s
KV-cache utilization: 0.93
Preemptions         : 0
```

Increasing the batch size beyond this point resulted in KV-cache saturation, sequence preemption, and lower generated-token goodput.

---

# Part C — Final Decision

The final recommendation is documented in:

```text
PartC/DECISION_MEMO.md
```

---

# Reproducing the Results

Run these commands from the repository root:

```powershell
python PartA\test_tokenizers.py
python PartA\benchmark_tokenizers.py
python PartA\compare_tokenizers.py

python PartB\calculate_kv_capacity.py
python PartB\analyze_bench.py
python PartB\check_reported_throughput.py
```

---

# Documentation

| File | Description |
|---|---|
| `REPORT.md` | Final corrected findings |
| `REPORT_v0.md` | Original report retained for audit/comparison |
| `NOTEBOOK.md` | Experiment and reproduction notes |
| `AI_USAGE.md` | AI usage disclosure |

---

## Key Takeaways

- Tokenization efficiency varies significantly by language and tokenizer.
- XLM-R substantially reduces token counts for the evaluated Indic languages compared with GPT-2.
- Theoretical KV-cache capacity does not equal the optimal serving batch size.
- Batch 24 was the best measured operating point for the tested long-context workload.
- `reported_tok_s` includes prompt processing and generated tokens, so it is not generation-only throughput.
