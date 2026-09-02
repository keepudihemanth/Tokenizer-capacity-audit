import unicodedata
import starter_kit.PartA.fertility as fertility
import tiktoken

enc = tiktoken.get_encoding("gpt2")

for name, path in [
    ("eng", "eng_sample.txt"),
    ("hin", "hin_sample.txt")
]:
    lines = fertility.read_lines(path)

    # read_lines already normalizes, so reload raw text for this test
    with open(path, "r", encoding="utf-8") as f:
        raw_lines = [
            line.strip()
            for line in f
            if line.strip()
        ]

    original_tokens = 0
    nfc_tokens = 0

    changed_lines = 0

    for line in raw_lines:
        nfc_line = unicodedata.normalize("NFC", line)

        if line != nfc_line:
            changed_lines += 1

        original_tokens += len(enc.encode(line))
        nfc_tokens += len(enc.encode(nfc_line))

    print(f"\n{name}")
    print("Lines changed by NFC:", changed_lines)
    print("Without NFC tokens   :", original_tokens)
    print("With NFC tokens      :", nfc_tokens)
    print("Difference           :", nfc_tokens - original_tokens)