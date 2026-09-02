# Part A — Tokenizer Recommendation Memo

## Headline

The original tokenizer conclusion based primarily on **tokens per whitespace word** is not sufficient for a multilingual routing or cost decision. Whitespace word counts are language-dependent and therefore do not hold the input content constant across English, Hindi, Telugu, and Kannada.

On a corrected evaluation corpus of **1,012 parallel sentences in each language**, GPT-2 produced substantially more tokens for the Indic languages than XLM-R:

| Language | GPT-2 tokens | XLM-R tokens | Token reduction with XLM-R |
| -------- | -----------: | -----------: | -------------------------: |
| English  |       27,044 |       30,661 |                    -13.37% |
| Hindi    |      200,467 |       38,222 |                     80.93% |
| Telugu   |      350,763 |       40,377 |                     88.49% |
| Kannada  |      367,405 |       41,482 |                     88.71% |

For equivalent parallel content, XLM-R uses dramatically fewer tokens for Hindi, Telugu, and Kannada. The result is consistent across the corrected corpus and is much stronger evidence for a routing or cost decision than the original smoke-test comparison.

## Routing Recommendation

**Do not route all languages through GPT-2-style tokenization when token count directly affects serving cost or context usage.** For Hindi, Telugu, and Kannada workloads, prefer an Indic/multilingual-aware tokenizer such as XLM-R where the downstream model and serving architecture allow it.

The single number I would use to drive a routing-and-cost decision is:

> **Total tokenizer tokens required for equivalent parallel sentences, reported as tokens per parallel sentence or total tokens over a fixed parallel corpus.**

This denominator is useful because each language expresses approximately the same underlying content for each aligned sentence. Unlike whitespace-word counts, it does not assume that word segmentation conventions are comparable across scripts.

## Biggest Caveat

This evaluation corpus is translated benchmark-style text and does not represent all production traffic. It cannot tell us how the tokenizers will behave on code-mixed language, informal chat, spelling variations, domain-specific vocabulary, user prompts, or other real production distributions. It also measures tokenizer efficiency, not model quality: fewer tokens alone does not prove that a model using that tokenizer will produce better answers.

## Production Metric

I would monitor **tokens per request grouped by detected language**, with the full distribution including median and high-percentile values.

A significant increase in token count for a particular language would indicate that the production input distribution differs from the evaluation corpus or that routing assumptions are no longer valid. This metric directly connects the tokenizer analysis to the actual quantities that affect context capacity and serving cost.
