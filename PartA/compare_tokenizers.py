from pathlib import Path
import json
# Paths

BASE_DIR = Path(__file__).resolve().parent
RESULTS_FILE = BASE_DIR / "benchmark_results.json"

# Load results
with open(RESULTS_FILE, "r", encoding="utf-8") as f:
    results = json.load(f)
# Compare token counts
print("Token reduction using XLM-R instead of GPT-2")
print("-" * 55)

for lang in ["eng", "hin", "tel", "kan"]:

    gpt2_tokens = results["gpt2"][lang]["tokens"]
    xlmr_tokens = results["xlm_roberta"][lang]["tokens"]

    reduction = (
        (gpt2_tokens - xlmr_tokens)/ gpt2_tokens* 100
    )

    print(
        f"{results['gpt2'][lang]['language']:10} "
        f"GPT-2: {gpt2_tokens:7} | "
        f"XLM-R: {xlmr_tokens:6} | "
        f"Reduction: {reduction:6.2f}%"
    )