# Tokenizer and Serving Capacity Evaluation

## Executive Summary

This evaluation investigated two questions:

1. How tokenizer choice affects token usage across English and Indic languages.
2. How concurrency and KV-cache pressure affect serving throughput for long-context requests.

The original draft findings were re-evaluated using controlled tokenizer experiments and the available serving benchmark data.

The main conclusions are:

- GPT-2 tokenization produces substantially more tokens for Hindi, Telugu, and Kannada than for English on the evaluation corpus.
- This disparity is **not an inherent property of Indic scripts**. Tokenizer choice materially changes the result.
- XLM-RoBERTa reduced total token counts by approximately 81–89% for the tested Indic languages relative to GPT-2, while using approximately 13% more tokens for English.
- The original whitespace-word fertility implementation had a denominator flaw caused by `split(" ")`, and the choice of denominator itself substantially affects cross-language ratios.
- For aligned multilingual text, tokens per parallel sentence is a more defensible comparison metric than tokens per whitespace word.
- In the long-context serving benchmark, `reported_tok_s` measures approximately total prompt plus generated tokens processed per second and should not be interpreted as completed-output throughput.
- Generated-token goodput peaked at batch 24 for the tested workload and decreased when KV-cache utilization approached saturation and sequence preemption began.

The recommended next step is a controlled production experiment using representative traffic before making permanent tokenizer-routing or infrastructure-capacity decisions.

---

# 1. Evaluation Scope

The evaluation consisted of:

1. Reproducing the original tokenizer fertility result.
2. Testing the effect of whitespace splitting.
3. Comparing average-of-ratios and ratio-of-totals aggregation.
4. Testing lowercasing and Unicode normalization.
5. Comparing denominator choices.
6. Building a multilingual evaluation corpus.
7. Comparing GPT-2 and XLM-RoBERTa tokenization.
8. Estimating KV-cache capacity from the model specification.
9. Reconciling the theoretical estimate with serving benchmark behavior.
10. Recomputing generated-token goodput from the benchmark log.
11. Determining what the benchmark's `reported_tok_s` metric counts.

---

# 2. Tokenizer Evaluation

## 2.1 Original Fertility Result

The original benchmark using GPT-2 reported:

| Language | Fertility (tokens/word) | Tokens/character |
|---|---:|---:|
| English | 1.27 | 0.226 |
| Hindi | 7.45 | 1.579 |

The resulting Hindi-to-English fertility ratio was:

```text
7.45 / 1.27 ≈ 5.89×
```

This demonstrates that GPT-2 tokenized the tested Hindi sample into substantially more tokens per whitespace-separated word than English.

However, this measurement alone does not establish that Hindi inherently requires approximately six times the serving cost across all tokenizers.

---

## 2.2 Whitespace Splitting

The original fertility calculation used:

```python
words = line.split(" ")
```

This can produce empty elements when multiple spaces occur.

For example:

```text
"Please keep the books  in the cupboard."
```

produces:

```python
line.split(" ")
```

with:

```text
['Please', 'keep', 'the', 'books', '', 'in', 'the', 'cupboard.']
```

This gives a word count of 8.

Using:

```python
line.split()
```

produces:

```text
['Please', 'keep', 'the', 'books', 'in', 'the', 'cupboard.']
```

which gives the correct whitespace-based count of 7.

A Hindi sample containing consecutive spaces similarly changed from:

```text
Old count: 6
New count: 5
```

This confirmed that the original implementation could artificially increase the word denominator.

---

## 2.3 Aggregation Choice

Two corpus-level aggregation methods were compared.

### Average of sentence-level ratios

```text
average(tokens_i / words_i)
```

### Ratio of corpus totals

```text
sum(tokens_i) / sum(words_i)
```

Results:

| Language | Average of ratios | Ratio of totals |
|---|---:|---:|
| English | 1.283063 | 1.269231 |
| Hindi | 7.598452 | 7.524590 |

The two methods differ because the first gives equal weight to every sentence while the second weights sentences according to their token and word counts.

For overall corpus-level token usage, the ratio of totals is generally easier to interpret.

---

## 2.4 Lowercasing and NFC Normalization

Lowercasing produced:

| Language | Original tokens | Lowercased tokens | Difference |
|---|---:|---:|---:|
| English | 96 | 99 | +3 |
| Hindi | 459 | 459 | 0 |

This shows that preprocessing can affect languages differently.

NFC normalization produced:

| Language | Lines changed | Token difference |
|---|---:|---:|
| English | 0 | 0 |
| Hindi | 0 | 0 |

No effect was observed on the tested smoke-test corpus.

---

## 2.5 Denominator Dependence

Using corrected corpus totals:

| Metric | English | Hindi |
|---|---:|---:|
| Tokens | 99 | 459 |
| Words | 78 | 61 |
| Characters | 448 | 290 |
| UTF-8 bytes | 448 | 764 |
| Sentences | 10 | 10 |

Hindi-to-English ratios changed depending on the denominator:

| Metric | Hindi/English ratio |
|---|---:|
| Tokens per word | 5.93× |
| Tokens per character | 7.16× |
| Tokens per UTF-8 byte | 2.72× |
| Tokens per sentence | 4.64× |

Therefore, the apparent magnitude of the cross-language disparity depends on the comparison metric.

A whitespace word is not a language-neutral unit of semantic content.

---

# 3. Multilingual Evaluation Corpus

A larger multilingual evaluation corpus was prepared from:

```text
openlanguagedata/flores_plus
```

using the:

```text
devtest
```

split.

The corpus included:

| Language | Configuration | Sentences |
|---|---|---:|
| English | eng_Latn | 1012 |
| Hindi | hin_Deva | 1012 |
| Telugu | tel_Telu | 1012 |
| Kannada | kan_Knda | 1012 |

Preprocessing:

- No lowercasing.
- No Unicode normalization.
- No punctuation removal.
- Original dataset text preserved.
- One sentence per line.

The aligned multilingual corpus provides a stronger basis for comparing token counts across languages.

---

# 4. GPT-2 vs XLM-RoBERTa

## 4.1 GPT-2 Results

| Language | Total Tokens | Tok/word | Tok/character | Tok/UTF-8 byte | Tok/sentence |
|---|---:|---:|---:|---:|---:|
| English | 27,044 | 1.234829 | 0.204932 | 0.204730 | 26.723320 |
| Hindi | 200,467 | 7.817611 | 1.529605 | 0.594729 | 198.089921 |
| Telugu | 350,763 | 20.708643 | 2.647867 | 0.991764 | 346.603755 |
| Kannada | 367,405 | 22.820186 | 2.661584 | 0.978755 | 363.048419 |

---

## 4.2 XLM-RoBERTa Results

| Language | Total Tokens | Tok/word | Tok/character | Tok/UTF-8 byte | Tok/sentence |
|---|---:|---:|---:|---:|---:|
| English | 30,661 | 1.399982 | 0.232340 | 0.232111 | 30.297431 |
| Hindi | 38,222 | 1.490543 | 0.291642 | 0.113394 | 37.768775 |
| Telugu | 40,377 | 2.383812 | 0.304801 | 0.114164 | 39.898221 |
| Kannada | 41,482 | 2.576522 | 0.300507 | 0.110507 | 40.990119 |

---

## 4.3 Token Count Change

| Language | GPT-2 Tokens | XLM-R Tokens | Change |
|---|---:|---:|---:|
| English | 27,044 | 30,661 | +13.37% |
| Hindi | 200,467 | 38,222 | -80.93% |
| Telugu | 350,763 | 40,377 | -88.49% |
| Kannada | 367,405 | 41,482 | -88.71% |

The multilingual tokenizer is therefore substantially more token-efficient for the tested Indic languages, while GPT-2 is more token-efficient for English in this corpus.

This demonstrates that tokenization cost is strongly tokenizer-dependent.

---

# 5. KV-Cache Capacity Analysis

The serving configuration used:

- 28 layers
- 8 KV heads
- Head dimension of 128
- FP16 KV-cache precision
- Separate storage for key and value
- Maximum sequence length of 4096 tokens
- 24 GB GPU memory
- 92% configured usable memory
- 1.6 GB assumed non-KV runtime overhead

KV-cache memory per token:

```text
28 × 8 × 128 × 2 × 2
= 114,688 bytes/token
```

This is approximately:

```text
112 KiB/token
```

KV-cache memory for one full 4096-token sequence:

```text
4096 × 114,688
= 469,762,048 bytes
≈ 0.4375 GiB
```

Estimated KV-cache memory budget:

```text
24 GB × 0.92
= 22.08 GB

22.08 GB − 1.6 GB
= 20.48 GB
```

Simplified theoretical capacity:

```text
≈ 46 full 4096-token sequences
```

This value should be interpreted as a theoretical upper bound rather than a guaranteed practical concurrency level.

---

# 6. Long-Context Serving Benchmark

The long-context workload used:

```text
Prompt length: 3584 tokens
Generation length: 512 tokens
Maximum sequence length: 4096 tokens
```

The results were:

| Batch | Wall Clock | Reported tok/s | Generated Goodput | TTFT p50 | ITL p50 | Preemptions | KV Utilization |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 4 | 28.98 s | 565.4 | 70.67 | 483.2 ms | 51.33 ms | 0 | 0.16 |
| 8 | 36.30 s | 902.6 | 112.84 | 519.0 ms | 62.26 ms | 0 | 0.31 |
| 16 | 49.97 s | 1311.4 | 163.94 | 498.3 ms | 77.20 ms | 0 | 0.62 |
| 24 | 61.16 s | 1607.4 | 200.92 | 500.5 ms | 96.07 ms | 0 | 0.93 |
| 32 | 94.71 s | 1384.0 | 172.99 | 636.9 ms | 101.79 ms | 7 | 0.97 |
| 48 | 151.41 s | 1298.5 | 162.31 | 955.4 ms | 100.00 ms | 23 | 0.97 |

---

# 7. Generated-Token Goodput

Generated-token goodput was calculated as:

```text
batch_size × generation_length / wall_clock_seconds
```

For batch 24:

```text
24 × 512
= 12,288 generated tokens

12,288 / 61.16
= 200.92 generated tokens/s
```

This was the highest observed generated-token goodput.

At higher concurrency:

```text
Batch 32: 172.99 generated tok/s
Batch 48: 162.31 generated tok/s
```

Therefore, increasing concurrency beyond batch 24 reduced completed-output throughput.

---

# 8. Interpretation of `reported_tok_s`

The benchmark's `reported_tok_s` was tested against total processed tokens.

For batch 24:

```text
24 × (3584 + 512)
= 98,304 total tokens
```

Dividing by wall-clock time:

```text
98,304 / 61.16
= 1607.33 tok/s
```

This matches:

```text
reported_tok_s = 1607.4
```

Therefore:

```text
reported_tok_s ≈
(prompt tokens + generated tokens) / wall-clock time
```

It should not be interpreted as generated-token goodput.

Both metrics may be useful:

- `reported_tok_s` describes total token processing rate.
- Generated-token goodput describes completed output throughput.

Capacity planning should clearly state which metric is being optimized.

---

# 9. Practical Capacity Boundary

The long-context benchmark shows a practical operating boundary.

At batch 24:

```text
Generated goodput = 200.92 tok/s
KV utilization    = 0.93
Preemptions       = 0
```

At batch 32:

```text
Generated goodput = 172.99 tok/s
KV utilization    = 0.97
Preemptions       = 7
```

At batch 48:

```text
Generated goodput = 162.31 tok/s
KV utilization    = 0.97
Preemptions       = 23
```

The data is consistent with the serving system reaching a practical KV-cache and scheduling limit between batch 24 and batch 32.

The simplified theoretical estimate of approximately 46 full sequences is therefore not equivalent to a recommended production concurrency.

---

# 10. Recommendations

## Tokenization

Do not use a fixed language-level cost multiplier based only on tokens per whitespace word.

Instead:

1. Measure token counts on aligned multilingual evaluation data.
2. Measure real production request token counts by language.
3. Evaluate multilingual tokenizer/model alternatives.
4. Validate output quality before changing model routing.
5. Measure actual latency and cost impact.

---

## Serving

For the tested:

```text
3584-token prompt + 512-token generation
```

workload:

```text
Recommended measured operating point: batch 24
```

This configuration achieved the highest observed generated-token goodput without recorded sequence preemptions.

Concurrency beyond this point should not be increased based on linear extrapolation.

---

# 11. Limitations

This evaluation has several limitations:

- The FLORES+ corpus is an evaluation corpus and may not represent production traffic.
- Token count does not directly equal total serving cost because compute, memory, batching, and model architecture also contribute.
- XLM-RoBERTa tokenization results do not automatically imply that XLM-RoBERTa is an appropriate replacement for a generative production model.
- The KV-cache capacity calculation uses an assumed runtime memory overhead and is therefore a theoretical approximation.
- The serving benchmark represents the tested hardware and workload configuration and should not automatically be generalized to other sequence lengths, models, GPUs, or serving engines.
- Model quality was not evaluated in the tokenizer benchmark.

---

# 12. Final Conclusion

The original draft correctly identified a large GPT-2 tokenization disparity between English and Indic-language text, but its explanation and production recommendation were too broad.

Tokenizer behavior is model-dependent, and a multilingual tokenizer dramatically reduced token counts for the tested Indic languages.

Similarly, the original serving interpretation was too optimistic because `reported_tok_s` counts total processed tokens and cannot be treated as completed-output throughput. The benchmark shows that generated-token goodput peaks at batch 24 for the tested long-context workload and decreases once KV-cache utilization approaches saturation and preemptions begin.

The evidence supports using tokenizer-aware measurements and generated-token goodput for future planning, followed by validation with representative production traffic before making permanent routing or infrastructure decisions.