import json

with open("benchmark_results.json", "r", encoding="utf-8") as f:
    results = json.load(f)

metrics = [
    "tok_per_word",
    "tok_per_character",
    "tok_per_utf8_byte",
    "tok_per_sentence",
]

for tokenizer_name, languages in results.items():

    print("\n" + "=" * 60)
    print(f"Tokenizer: {tokenizer_name}")
    print("Ratios relative to English")
    print("=" * 60)

    english = languages["eng"]

    for lang in ["hin", "tel", "kan"]:

        print(f"\n{languages[lang]['language']} vs English")

        for metric in metrics:

            ratio = (
                languages[lang][metric]/ english[metric]
            )

            print(
                f"{metric:22}: "
                f"{ratio:.3f}x"
            )