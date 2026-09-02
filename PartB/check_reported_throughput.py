import csv

with open("bench/bench_log.csv", newline="") as f:
    rows = list(csv.DictReader(f))

print("CHECKING WHAT reported_tok_s COUNTS")
print("=" * 75)

for row in rows:
    if int(row["prompt_len"]) != 3584:
        continue

    batch = int(row["batch_size"])
    prompt = int(row["prompt_len"])
    gen = int(row["gen_len"])
    wall = float(row["wall_clock_s"])
    reported = float(row["reported_tok_s"])

    generated = batch * gen
    prompt_tokens = batch * prompt
    total_tokens = batch * (prompt + gen)

    gen_rate = generated / wall
    prompt_rate = prompt_tokens / wall
    total_rate = total_tokens / wall

    print(f"\nBatch {batch}")
    print(f"Reported tok/s       : {reported:.2f}")
    print(f"Generated-only tok/s : {gen_rate:.2f}")
    print(f"Prompt-only tok/s    : {prompt_rate:.2f}")
    print(f"Total tokens / s     : {total_rate:.2f}")
    print(f"Reported / goodput   : {reported / gen_rate:.2f}x")