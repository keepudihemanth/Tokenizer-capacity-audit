# Chronological Lab Notebook

## Experiment A2-01 — Reproduce the Original Tokenizer Benchmark

**Hypothesis:** The numbers in `REPORT_v0.md` can be reproduced using the provided `fertility.py` script and sample corpora.

**Command:**

```bash
python fertility.py
```

**Result:**

| Language | Fertility (tok/word) | Tok/char |
|---|---:|---:|
| English | 1.27 | 0.226 |
| Hindi | 7.45 | 1.579 |

Hindi/English fertility ratio: **5.89×**.

**Conclusion:** The original benchmark is reproducible. This verifies that the report's tokenizer numbers were produced by the provided script, but does not verify that the metric or recommendation is correct.

---

## Experiment A2-02 — Test Whitespace Word Splitting

**Hypothesis:** `line.split(" ")` incorrectly counts empty strings as words when consecutive spaces occur.

**Isolation test:**

```text
split(" ") → 8 words
split()     → 7 words
```

A Hindi sample line containing consecutive spaces produced:

```text
Old count: 6
New count: 5
```

**Baseline result using `split(" ")`:**

- English fertility: **1.27**
- Hindi fertility: **7.45**
- Hindi/English ratio: **5.89×**

**After changing only the word split to `split()`:**

- English fertility: **1.28**
- Hindi fertility: **7.60**
- Hindi/English ratio: **5.92×**

**Conclusion:** `split(" ")` is a verified implementation flaw because consecutive spaces increase the denominator with an empty element. This artificially lowers fertility. On the provided sample, the distortion is small but measurable.

---

## Experiment A2-03 — Average of Ratios vs Ratio of Totals

**Hypothesis:** Averaging sentence-level fertility values gives a different result from corpus-level total tokens divided by total words.

**Experiment:** Compared:

```text
average(tokens_i / words_i)
```

with:

```text
sum(tokens_i) / sum(words_i)
```

**Results:**

| Language | Average of ratios | Ratio of totals | Difference |
|---|---:|---:|---:|
| English | 1.283063 | 1.269231 | +0.013832 |
| Hindi | 7.598452 | 7.524590 | +0.073862 |

**Conclusion:** The two calculations answer different questions. The original calculation weights every sentence equally, while the ratio of totals represents corpus-level token usage per word. On this sample, the original aggregation overestimates both values by approximately 1%.

---

## Experiment A2-04 — Test Lowercasing

**Hypothesis:** Lowercasing may affect token counts differently across languages.

**Results:**

| Language | Original tokens | Lowercased tokens | Difference |
|---|---:|---:|---:|
| English | 96 | 99 | +3 |
| Hindi | 459 | 459 | 0 |

**Conclusion:** Lowercasing changes English token counts by **+3.13%** on the provided sample while leaving Hindi unchanged. Therefore, lowercasing can asymmetrically affect a cross-language comparison and should not be silently applied without justification.

---

## Experiment A2-05 — Test NFC Normalization

**Hypothesis:** Unicode NFC normalization may change the corpus or tokenizer results.

**Results:**

| Language | Lines changed | Tokens without NFC | Tokens with NFC | Difference |
|---|---:|---:|---:|---:|
| English | 0 | 96 | 96 | 0 |
| Hindi | 0 | 459 | 459 | 0 |

**Conclusion:** NFC normalization had no measurable effect on the provided smoke-test corpus. It is therefore harmless for this corpus, although this experiment does not prove that NFC normalization is unnecessary for all corpora.

---

## Experiment A2-06 — Test Denominator Dependence

**Hypothesis:** The apparent cross-language tokenizer disadvantage changes depending on the denominator.

**Corrected corpus totals:**

| Metric | English | Hindi |
|---|---:|---:|
| Tokens | 99 | 459 |
| Words | 78 | 61 |
| Characters | 448 | 290 |
| UTF-8 bytes | 448 | 764 |
| Sentences | 10 | 10 |

**Hindi relative to English:**

| Denominator | Hindi/English ratio |
|---|---:|
| Tokens per word | 5.93× |
| Tokens per character | 7.16× |
| Tokens per UTF-8 byte | 2.72× |
| Tokens per sentence | 4.64× |

**Conclusion:** The same underlying token counts produce substantially different cross-language ratios depending on the denominator. A denominator must therefore be selected based on what is intended to remain comparable across languages.

**Conceptual flaw identified:** Tokens per whitespace word is not a language-neutral measure of tokenizer efficiency. The code can compute this metric correctly while the metric itself remains unsuitable as the primary basis for cross-language routing and cost decisions, because whitespace word counts do not hold equivalent content constant across languages.

---

# Part A1 — Multilingual Evaluation Corpus

## Dead End — Initial Corpus Download Attempt

**Attempt:** Load the multilingual evaluation corpus directly using `prepare_corpus.py`.

**Result:** The initial request failed because the Hugging Face dataset required authenticated access.

**Revision:** I resolved the dataset access issue and reran the corpus preparation script successfully.

**Why this matters:** The failed attempt changed the corpus preparation workflow, so it is included rather than being removed from the chronological record.

---

## Experiment A1-01 — Build Evaluation Corpus

**Dataset:** `openlanguagedata/flores_plus`

**Split:** `devtest`

**Languages:**

- English (`eng_Latn`)
- Hindi (`hin_Deva`)
- Telugu (`tel_Telu`)
- Kannada (`kan_Knda`)

**Command:**

```bash
python prepare_corpus.py
```

**Result:**

| Language | Sentences |
|---|---:|
| English | 1012 |
| Hindi | 1012 |
| Telugu | 1012 |
| Kannada | 1012 |

**Preprocessing:**

- No lowercasing
- No Unicode normalization
- No punctuation removal
- One sentence per line
- Original dataset text preserved

**Conclusion:** The evaluation corpus contains 1012 sentences for each of four languages, including English, Hindi, Telugu, and Kannada.

**Caveat:** This corpus is useful for aligned cross-language comparison, but it cannot fully represent production traffic such as conversational inputs, code-mixed language, regional writing variation, or domain-specific requests.

---

# Experiment A3-01 — Full Multilingual Tokenizer Benchmark

**Hypothesis:** A multilingual tokenizer will produce more consistent token counts across Indic languages than GPT-2.

**Tokenizers:**

- GPT-2 tokenizer
- XLM-RoBERTa tokenizer

**Corpus:** 1012 sentences × 4 languages.

**Command:**

```bash
python benchmark_tokenizers.py
```

## GPT-2 Results

| Language | Tokens | Tok/word | Tok/character | Tok/UTF-8 byte | Tok/sentence |
|---|---:|---:|---:|---:|---:|
| English | 27,044 | 1.234829 | 0.204932 | 0.204730 | 26.723320 |
| Hindi | 200,467 | 7.817611 | 1.529605 | 0.594729 | 198.089921 |
| Telugu | 350,763 | 20.708643 | 2.647867 | 0.991764 | 346.603755 |
| Kannada | 367,405 | 22.820186 | 2.661584 | 0.978755 | 363.048419 |

## XLM-RoBERTa Results

| Language | Tokens | Tok/word | Tok/character | Tok/UTF-8 byte | Tok/sentence |
|---|---:|---:|---:|---:|---:|
| English | 30,661 | 1.399982 | 0.232340 | 0.232111 | 30.297431 |
| Hindi | 38,222 | 1.490543 | 0.291642 | 0.113394 | 37.768775 |
| Telugu | 40,377 | 2.383812 | 0.304801 | 0.114164 | 39.898221 |
| Kannada | 41,482 | 2.576522 | 0.300507 | 0.110507 | 40.990119 |

**Conclusion:** The multilingual tokenizer produced much more consistent sentence-level token counts across Hindi, Telugu, and Kannada than GPT-2.

---

# Experiment A3-02 — Tokenizer Efficiency Comparison

**Experiment:** Compare total token counts from the two tokenizers.

**Results:**

| Language | Change using XLM-R instead of GPT-2 |
|---|---:|
| English | 13.37% more tokens |
| Hindi | 80.93% fewer tokens |
| Telugu | 88.49% fewer tokens |
| Kannada | 88.71% fewer tokens |

**Conclusion:** XLM-RoBERTa is not universally more token-efficient: it uses 13.37% more tokens for English on this corpus. However, it reduces token counts by approximately 81–89% for the three tested Indic languages.

---

# Current Decision Hypothesis

For the parallel offline evaluation corpus, **tokens per parallel sentence** is the strongest single comparison metric because corresponding sentence positions represent approximately the same content across languages.

This is an evaluation metric, not automatically a production metric. In production, token usage should be monitored per real request, grouped by language and combined with actual latency and cost measurements.

---

# Part B — Capacity Reconciliation

## Experiment B1-01 — Calculate KV-Cache Capacity

**Hypothesis:** The model specification should allow us to estimate the maximum number of concurrent full-length 4096-token sequences before KV-cache memory becomes the limiting factor.

**Inputs from `model_spec.md`:**

- Layers: 28
- KV heads: 8
- Head dimension: 128
- KV-cache precision: FP16 = 2 bytes/value
- K and V stored separately
- GPU memory: 24 GB
- GPU memory utilization: 0.92
- Assumed non-KV runtime overhead: 1.6 GB
- Maximum sequence length: 4096 tokens

**Command:**

```bash
python calculate_kv_capacity.py
```

### KV-Cache Bytes per Token

```text
28 layers
× 8 KV heads
× 128 dimensions
× 2 (K and V)
× 2 bytes per FP16 value
= 114,688 bytes/token
= 112 KiB/token
```

### KV-Cache Bytes per 4096-Token Sequence

```text
4096 × 114,688
= 469,762,048 bytes
= 0.4375 GiB
```

### Available KV-Cache Memory

```text
24 GB × 0.92 = 22.08 GB usable memory

22.08 GB − 1.6 GB runtime overhead
= 20.48 GB KV-cache budget
```

### Predicted Capacity

```text
KV-cache budget / memory per sequence
≈ 46 whole 4096-token sequences
```

**Result:** The simplified memory calculation predicts a theoretical upper bound of **46 concurrent full-length 4096-token sequences**.

**Caveat:** The estimate of 46 sequences is a simplified theoretical upper bound based on the assumed memory budget. The benchmark log is stronger evidence for practical capacity because the serving system also has scheduler behavior and memory overheads not captured by the simplified calculation.

---

## Experiment B1-02 — Check Prediction Against the Benchmark Log

**Hypothesis:** As long-context concurrency approaches the practical KV-cache capacity, KV-cache utilization should increase and the scheduler should begin preempting sequences.

**Relevant workload:**

```text
3584 prompt tokens + 512 generated tokens
= 4096 maximum tokens per sequence
```

**Observed results:**

| Batch | KV-cache utilization | Preempted sequences |
|---:|---:|---:|
| 4 | 0.16 | 0 |
| 8 | 0.31 | 0 |
| 16 | 0.62 | 0 |
| 24 | 0.93 | 0 |
| 32 | 0.97 | 7 |
| 48 | 0.97 | 23 |

**Conclusion:** The benchmark reaches a practical memory/scheduler capacity boundary between batch 24 and batch 32. The theoretical estimate of 46 sequences is an upper bound based on simplified memory assumptions; the scheduler experiences pressure earlier in the real serving configuration.

---

## Experiment B2-01 — Recompute Long-Context Generated-Token Goodput

**Hypothesis:** Increasing batch size beyond a certain point does not continue to improve completed-output throughput.

**Command:**

```bash
python analyze_bench.py
```

**Results:**

| Batch | Generated tokens | Wall-clock time | Generated-token goodput | Preempted sequences | KV utilization |
|---:|---:|---:|---:|---:|---:|
| 4 | 2,048 | 28.98 s | 70.67 tok/s | 0 | 0.16 |
| 8 | 4,096 | 36.30 s | 112.84 tok/s | 0 | 0.31 |
| 16 | 8,192 | 49.97 s | 163.94 tok/s | 0 | 0.62 |
| 24 | 12,288 | 61.16 s | 200.92 tok/s | 0 | 0.93 |
| 32 | 16,384 | 94.71 s | 172.99 tok/s | 7 | 0.97 |
| 48 | 24,576 | 151.41 s | 162.31 tok/s | 23 | 0.97 |

**Key comparison:**

```text
Batch 24: 200.92 generated tok/s
Batch 32: 172.99 generated tok/s
```

Increasing the batch from 24 to 32 increased concurrency by 33.3% but reduced generated-token goodput by approximately 13.9%.

At the same point:

```text
KV utilization: 0.93 → 0.97
Preempted sequences: 0 → 7
```

**Conclusion:** The measured throughput drop is associated with KV-cache saturation and scheduler preemption.

**Proposed configuration change:** Cap this 3584-token prompt workload at **batch 24** rather than allowing batches of 32 or 48.

**Measured effect:**

```text
Batch 24 goodput: 200.92 tok/s
Batch 48 goodput: 162.31 tok/s
```

Batch 24 delivers approximately **23.8% higher generated-token goodput than batch 48** for this workload.

---

## Experiment B3-01 — Determine What `reported_tok_s` Measures

**Hypothesis:** The harness's `reported_tok_s` counts both prompt and generated tokens rather than completed generated output alone.

**Command:**

```bash
python check_reported_throughput.py
```

### Batch-24 Evidence

Total processed tokens:

```text
24 × (3584 + 512)
= 98,304 tokens
```

Total-token throughput:

```text
98,304 / 61.16
= 1607.33 tok/s
```

This matches the logged value:

```text
reported_tok_s = 1607.4 tok/s
```

Completed generated tokens:

```text
24 × 512
= 12,288 tokens
```

Generated-token goodput:

```text
12,288 / 61.16
= 200.92 tok/s
```

### Independent Derivation

Each request has:

```text
512 output tokens
4096 total prompt + output tokens
```

Therefore:

```text
Output fraction = 512 / 4096
                = 1 / 8
```

So:

```text
1607.4 × 1/8
= 200.93 tok/s
```

The small difference from 200.92 tok/s is due to rounding.

**Conclusion:** `reported_tok_s` measures approximately **prompt tokens plus generated tokens processed per second**, not completed-output goodput.

---

## Experiment B3-02 — Test the Report's Throughput Conclusion

The original report compared:

```text
Long prompt, batch 16: 1311 tok/s
Short prompt, batch 16: 883 tok/s
```

and concluded that longer prompts provide better throughput.

The experiment above shows that these values count total processed tokens, including the much larger prompt.

For long prompts:

```text
reported tok/s = 1311.4
generated-token goodput = 163.94 tok/s
```

Therefore, the reported comparison does not establish that longer prompts improve completed-output serving capacity.

The report also projected approximately 3200 tok/s at batch 48 by scaling throughput linearly. The actual batch-48 row reports only:

```text
1298.5 reported tok/s
162.31 generated-token goodput
23 preempted sequences
```

**Conclusion:** The honest report should have stated that total processed-token throughput increases initially with concurrency but generated-token goodput peaks at batch 24 and decreases when KV-cache pressure and preemption begin. Linear scaling to batch 48 is not supported by the measured data.

---

## Experiment B4-01 — Metric to Confirm the B2 Mechanism

**Metric selected:** KV-cache utilization.

**Prediction:** KV-cache utilization should approach saturation at the same point where generated-token goodput stops improving and scheduler preemption begins.

**Observed evidence:**

```text
Batch 24:

KV utilization = 0.93
Preemptions = 0
Goodput = 200.92 tok/s


Batch 32:

KV utilization = 0.97
Preemptions = 7
Goodput = 172.99 tok/s


Batch 48:

KV utilization = 0.97
Preemptions = 23
Goodput = 162.31 tok/s
```

**Conclusion:** I expect the serving stack's KV-cache utilization counter to remain near saturation, approximately **97%**, when additional concurrency no longer improves throughput. The observed log behavior supports this prediction.

---

## Part C Note

Part C is intentionally not presented as an experiment in this notebook because the proposed Day-1 experiment was not actually run.

The decision memo documents the assumptions, arithmetic, success metric, and kill criterion without presenting unrun experiments as completed results.