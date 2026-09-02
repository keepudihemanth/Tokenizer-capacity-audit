from datasets import load_dataset
from pathlib import Path
import json

LANGUAGES = {
    "eng": "eng_Latn",
    "hin": "hin_Deva",
    "tel": "tel_Telu",
    "kan": "kan_Knda",
}

SPLIT = "devtest"

OUTPUT_DIR = Path("eval_corpus")
OUTPUT_DIR.mkdir(exist_ok=True)

metadata = {
    "dataset": "openlanguagedata/flores_plus",
    "split": SPLIT,
    "languages": {},
    "preprocessing": [
        "No lowercasing",
        "No Unicode normalization",
        "No punctuation removal",
        "Original dataset text written one sentence per line",
    ],
}

for short_name, config in LANGUAGES.items():
    print(f"\nLoading {config}...")

    dataset = load_dataset(
        "openlanguagedata/flores_plus",
        config,
        split=SPLIT
    )

    output_file = OUTPUT_DIR / f"{short_name}.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        for row in dataset:
            f.write(row["text"].strip() + "\n")

    metadata["languages"][short_name] = {
        "config": config,
        "sentences": len(dataset),
        "file": str(output_file)
    }

    print(f"Saved {len(dataset)} sentences → {output_file}")

with open(
    OUTPUT_DIR / "metadata.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(metadata, f, ensure_ascii=False, indent=2)

print("\nDone.")