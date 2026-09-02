import starter_kit.PartA.fertility as fertility

for name, path in [
    ("eng", "eng_sample.txt"),
    ("hin", "hin_sample.txt")
]:
    lines = fertility.read_lines(path)

    print(f"\n{name}")

    for i, line in enumerate(lines):
        old_count = len(line.split(" "))
        new_count = len(line.split())

        if old_count != new_count:
            print(f"Line {i + 1}")
            print("Old:", old_count)
            print("New:", new_count)
            print("Text:", repr(line))