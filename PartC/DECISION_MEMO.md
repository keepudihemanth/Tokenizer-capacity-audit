# Decision Memo — Tokenizer and Serving Capacity

## Executive Summary

The original findings in `REPORT_v0.md` should not be used as the basis for production routing or capacity planning without revision.

The investigation produced two main findings:

1. **Tokenizer comparison:** GPT-2 produces substantially more tokens for the tested Indic languages than XLM-RoBERTa, but the original claim that Hindi is inherently 6× more expensive because of its script is not supported. The result depends strongly on the tokenizer and the metric used.

2. **Serving capacity:** The reported `reported_tok_s` metric includes both prompt and generated tokens. It is therefore not equivalent to completed-output throughput. For the long-context workload, generated-token goodput peaks at batch 24 and decreases when KV-cache utilization approaches saturation and sequence preemption begins.

The recommended decisions are:

- Do not use the original Hindi 6× cost multiplier for production planning.
- Prefer a multilingual tokenizer/model stack for workloads where Indic-language token efficiency is important, subject to model-quality validation.
- Cap the tested long-context workload at approximately batch 24 rather than scaling concurrency linearly.
- Run a controlled Day-1 production experiment before making permanent routing or capacity decisions.

---

# Part A — Tokenizer Decision

## Decision

Do not adopt the conclusion from `REPORT_v0.md` that Hindi requests should automatically be budgeted at 6× the cost of English requests.

The original fertility comparison correctly demonstrated that GPT-2 tokenizes the tested Hindi corpus into substantially more tokens than English. However, the conclusion that this is an inherent property of Hindi or that every tokenizer will have the same behavior is not supported.

A tokenizer comparison using the same aligned multilingual corpus showed that XLM-RoBERTa substantially reduces token counts for Hindi, Telugu, and Kannada relative to GPT-2.

---

## Evidence

### GPT-2 Total Tokens

| Language | Total Tokens |
|---|---:|
| English | 27,044 |
| Hindi | 200,467 |
| Telugu | 350,763 |
| Kannada | 367,405 |

### XLM-RoBERTa Total Tokens

| Language | Total Tokens |
|---|---:|
| English | 30,661 |
| Hindi | 38,222 |
| Telugu | 40,377 |
| Kannada | 41,482 |

### Change Using XLM-R Instead of GPT-2

| Language | Token Change |
|---|---:|
| English | 13.37% more tokens |
| Hindi | 80.93% fewer tokens |
| Telugu | 88.49% fewer tokens |
| Kannada | 88.71% fewer tokens |

The tokenizer therefore materially changes the observed cross-language token cost.

---

## Interpretation

The original GPT-2 benchmark measured a real tokenizer behavior, but it should not have been generalized into the statement that Indic scripts inherently require proportionally higher tokenization cost for every tokenizer.

The denominator also affects the measured disparity. Tokens per word, tokens per character, tokens per UTF-8 byte, and tokens per sentence produce different ratios.

For the aligned evaluation corpus, tokens per parallel sentence is the strongest single comparison because corresponding sentence positions represent approximately the same content across languages.

---

## Recommendation

For workloads with substantial Indic-language traffic:

1. Evaluate multilingual tokenizer/model options.
2. Measure model quality before switching production traffic.
3. Measure real request-level token counts by language.
4. Measure latency and infrastructure cost using representative production traffic.
5. Avoid applying a fixed language-level cost multiplier based only on a whitespace-word fertility calculation.

The benchmark supports further evaluation of multilingual tokenization, but it does not by itself prove that a particular tokenizer/model should replace a production model.

---

# Part B — Serving Capacity Decision

## Decision

For the tested workload consisting of:

```text
Prompt length: 3584 tokens
Generation length: 512 tokens
Maximum sequence length: 4096 tokens
```

the recommended operating point is **batch 24**.

Increasing concurrency beyond this point caused generated-token goodput to decrease while KV-cache utilization reached saturation and the serving system began preempting sequences.

---

## KV-Cache Capacity Estimate

The model specification used:

- 28 layers
- 8 KV heads
- 128 head dimension
- FP16 KV-cache values
- Separate key and value storage

KV-cache memory per token:

```text
28 × 8 × 128 × 2 × 2
= 114,688 bytes per token
```

For a 4096-token sequence:

```text
4096 × 114,688
= 469,762,048 bytes
≈ 0.4375 GiB
```

Using the assumed memory budget:

```text
24 GB × 0.92
= 22.08 GB usable GPU memory

22.08 GB − 1.6 GB runtime overhead
= 20.48 GB estimated KV-cache budget
```

This gives a simplified theoretical upper bound of approximately:

```text
46 full 4096-token sequences
```

This estimate should be treated as an upper bound rather than a practical concurrency target because real serving capacity also depends on scheduler behavior and additional runtime overhead.

---

## Benchmark Evidence

### Long-Context Workload

| Batch | Generated-Token Goodput | KV Utilization | Preempted Sequences |
|---:|---:|---:|---:|
| 4 | 70.67 tok/s | 0.16 | 0 |
| 8 | 112.84 tok/s | 0.31 | 0 |
| 16 | 163.94 tok/s | 0.62 | 0 |
| 24 | 200.92 tok/s | 0.93 | 0 |
| 32 | 172.99 tok/s | 0.97 | 7 |
| 48 | 162.31 tok/s | 0.97 | 23 |

The maximum measured generated-token goodput occurred at batch 24.

---

## Why Batch 24 Is Preferred

Batch 24:

```text
Generated-token goodput = 200.92 tok/s
KV-cache utilization    = 0.93
Preempted sequences     = 0
```

Batch 32:

```text
Generated-token goodput = 172.99 tok/s
KV-cache utilization    = 0.97
Preempted sequences     = 7
```

Batch 48:

```text
Generated-token goodput = 162.31 tok/s
KV-cache utilization    = 0.97
Preempted sequences     = 23
```

Increasing the batch beyond 24 does not improve completed-output throughput for this workload.

The evidence is consistent with the serving system approaching practical KV-cache capacity, after which preemption and scheduling overhead reduce useful output throughput.

---

# Part B — Throughput Metric Correction

## Finding

`reported_tok_s` does not represent generated-token goodput.

For the batch-24 long-context workload:

```text
24 requests
× (3584 prompt tokens + 512 generated tokens)
= 98,304 total processed tokens
```

Using the wall-clock time:

```text
98,304 / 61.16
= 1607.33 tok/s
```

This matches the logged:

```text
reported_tok_s = 1607.4 tok/s
```

However, completed generated tokens are:

```text
24 × 512
= 12,288 generated tokens
```

Therefore:

```text
12,288 / 61.16
= 200.92 generated tok/s
```

---

## Decision

Capacity planning should not use `reported_tok_s` alone as the measure of completed-output capacity.

For this benchmark:

- `reported_tok_s` measures approximately total prompt plus generated tokens processed per second.
- Generated-token goodput measures completed generated output per second.

Both metrics can be useful, but they answer different questions.

---

# Rejected Conclusion

The original report stated that longer prompts clearly improve GPU utilization and that throughput could scale linearly to approximately 3200 tok/s at batch 48.

The measured data does not support linear scaling.

The actual batch-48 result was:

```text
reported_tok_s           = 1298.5 tok/s
generated-token goodput  = 162.31 tok/s
preempted sequences      = 23
KV-cache utilization     = 0.97
```

The practical operating region was reached before batch 48.

---

# Part C — Day-1 Production Experiment

## Objective

Validate the tokenizer and serving-capacity conclusions using representative production traffic before making permanent infrastructure or routing decisions.

---

## Experiment Design

Run two controlled configurations using comparable traffic:

### Configuration A — Current Baseline

- Current tokenizer/model configuration
- Existing production routing
- Current concurrency configuration

### Configuration B — Candidate Configuration

- Multilingual tokenizer/model configuration where applicable
- Long-context concurrency capped near the measured safe operating point
- Same request distribution and evaluation period

The experiment should use representative requests containing English and Indic-language traffic where available.

---

## Primary Success Metrics

Measure:

1. **Generated-token goodput**
2. **End-to-end latency**
3. **Time to first token**
4. **KV-cache utilization**
5. **Sequence preemptions**
6. **Tokens processed per request**
7. **Model output quality or task success**

---

## Primary Serving Success Criterion

The candidate configuration should demonstrate one of the following without unacceptable quality or latency regression:

- Higher generated-token goodput at the same hardware cost, or
- Lower latency at comparable goodput, or
- Lower token usage for Indic-language requests while maintaining output quality.

---

## Kill Criterion

Stop or reject the candidate configuration if:

1. Output quality shows a meaningful regression.
2. End-to-end latency materially worsens without compensating throughput improvement.
3. Generated-token goodput does not improve despite increased complexity.
4. KV-cache pressure or sequence preemption increases enough to reduce completed-output performance.
5. Token reduction does not produce a meaningful serving or cost benefit.

---

# Day-1 Decision Rule

After the experiment:

### Adopt the candidate configuration if:

- Output quality is maintained.
- Generated-token goodput or latency improves.
- Indic-language token usage decreases enough to provide measurable serving benefits.
- KV-cache pressure remains within a stable operating range.

### Keep the current configuration if:

- Token savings do not translate into serving benefits.
- Model quality regresses.
- Latency or preemption increases.
- Operational complexity exceeds the measured benefit.

---

# Final Recommendation

The current evidence supports two immediate changes in how the system should be evaluated:

1. **Tokenizer decisions should be based on aligned multilingual token measurements and production request data, rather than assuming a fixed cost multiplier for a language based on whitespace-word fertility.**

2. **Serving capacity should be planned using generated-token goodput and real KV-cache behavior, rather than extrapolating total-token throughput linearly with batch size.**

For the tested 3584-token prompt and 512-token generation workload, batch 24 is the best measured operating point in the available benchmark data.

The next step is to validate these findings with representative Day-1 traffic before making permanent routing, tokenizer, or hardware-capacity decisions.