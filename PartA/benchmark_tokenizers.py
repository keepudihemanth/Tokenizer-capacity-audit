from pathlib import Path
import json

import tiktoken
from transformers import AutoTokenizer


# Paths
BASE_DIR = Path(__file__).resolve().parent

CORPUS_DIR = BASE_DIR / "eval_corpus"
OUTPUT_FILE = BASE_DIR / "benchmark_results.json"

LANGUAGES = {
    "eng": "English",
    "hin": "Hindi",
    "tel": "Telugu",
    "kan": "Kannada",
}
# Load tokenizers
print("Loading tokenizers...")
gpt2 = tiktoken.get_encoding("gpt2")
xlmr = AutoTokenizer.from_pretrained(
    "xlm-roberta-base"
)

tokenizers = {
    "gpt2": lambda text: gpt2.encode(text),
    "xlm_roberta": lambda text: xlmr.encode(
        text,
        add_special_tokens=False
    ),
}


results = {}


# Benchmark

for tokenizer_name, tokenize in tokenizers.items():

    print(f"\n{'=' * 50}")
    print(f"Tokenizer: {tokenizer_name}")
    print(f"{'=' * 50}")

    results[tokenizer_name] = {}

    for lang_code, lang_name in LANGUAGES.items():

        file_path = CORPUS_DIR / f"{lang_code}.txt"

        with open(file_path, "r", encoding="utf-8") as f:
            lines = [
                line.rstrip("\n")
                for line in f
                if line.strip()
            ]

        total_tokens = 0
        total_words = 0
        total_chars = 0
        total_bytes = 0

        for line in lines:

            # IMPORTANT:
            # No lowercasing.
            # No Unicode normalization.
            # No punctuation removal.
            # Tokenize corpus text as prepared.

            tokens = tokenize(line)

            total_tokens += len(tokens)
            total_words += len(line.split())
            total_chars += len(line)
            total_bytes += len(line.encode("utf-8"))

        sentence_count = len(lines)

        metrics = {
            "language": lang_name,
            "sentences": sentence_count,
            "tokens": total_tokens,
            "words": total_words,
            "characters": total_chars,
            "utf8_bytes": total_bytes,
            "tok_per_word": total_tokens / total_words,
            "tok_per_character": total_tokens / total_chars,
            "tok_per_utf8_byte": total_tokens / total_bytes,
            "tok_per_sentence": total_tokens / sentence_count,
        }

        results[tokenizer_name][lang_code] = metrics

        print(f"\n{lang_name}")
        print(f"Sentences       : {sentence_count}")
        print(f"Total tokens    : {total_tokens}")
        print(f"Tok / word      : {metrics['tok_per_word']:.6f}")
        print(f"Tok / character : {metrics['tok_per_character']:.6f}")
        print(f"Tok / UTF-8 byte: {metrics['tok_per_utf8_byte']:.6f}")
        print(f"Tok / sentence  : {metrics['tok_per_sentence']:.6f}")


# Save exact results

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(
        results,
        f,
        ensure_ascii=False,
        indent=2
    )

print("\nBenchmark complete.")
print(f"Results saved to: {OUTPUT_FILE}")