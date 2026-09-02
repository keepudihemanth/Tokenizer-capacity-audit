import starter_kit.PartA.fertility as fertility
import tiktoken

enc = tiktoken.get_encoding("gpt2")

for name, path in [
    ("eng", "eng_sample.txt"),
    ("hin", "hin_sample.txt")
]:
    lines = fertility.read_lines(path)

    total_tokens = 0
    total_words = 0
    total_chars = 0
    total_bytes = 0

    for line in lines:
        line = line.lower()

        total_tokens += len(enc.encode(line))
        total_words += len(line.split())
        total_chars += len(line)
        total_bytes += len(line.encode("utf-8"))

    print(f"\n{name}")
    print("Tokens:", total_tokens)
    print("Words:", total_words)
    print("Characters:", total_chars)
    print("UTF-8 bytes:", total_bytes)

    print("\nTok/word :", total_tokens / total_words)
    print("Tok/char :", total_tokens / total_chars)
    print("Tok/byte :", total_tokens / total_bytes)
    print("Tok/sentence:", total_tokens / len(lines))