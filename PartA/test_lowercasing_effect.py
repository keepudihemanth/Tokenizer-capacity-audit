import starter_kit.PartA.fertility as fertility
import tiktoken

enc = tiktoken.get_encoding("gpt2")

for name, path in [
    ("eng", "eng_sample.txt"),
    ("hin", "hin_sample.txt")
]:
    lines = fertility.read_lines(path)

    original_tokens = 0
    lower_tokens = 0

    for line in lines:
        original_tokens += len(enc.encode(line))
        lower_tokens += len(enc.encode(line.lower()))

    print(f"\n{name}")
    print("Original tokens :", original_tokens)
    print("Lowercase tokens:", lower_tokens)
    print("Difference      :", lower_tokens - original_tokens)