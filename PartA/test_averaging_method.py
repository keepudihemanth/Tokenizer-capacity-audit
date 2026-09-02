import starter_kit.PartA.fertility as fertility
import tiktoken

enc = tiktoken.get_encoding("gpt2")

for name, path in [
    ("eng", "eng_sample.txt"),
    ("hin", "hin_sample.txt")
]:
    lines = fertility.read_lines(path)

    per_line_fertility = []

    total_tokens = 0
    total_words = 0

    for line in lines:
        line = line.lower()

        tokens = enc.encode(line)
        words = line.split()

        per_line_fertility.append(
            len(tokens) / len(words)
        )

        total_tokens += len(tokens)
        total_words += len(words)

    average_of_ratios = (
        sum(per_line_fertility) / len(per_line_fertility)
    )

    ratio_of_totals = (
        total_tokens / total_words
    )

    print(f"\n{name}")
    print("Average of ratios :", average_of_ratios)
    print("Ratio of totals   :", ratio_of_totals)
    print("Difference        :", average_of_ratios - ratio_of_totals)