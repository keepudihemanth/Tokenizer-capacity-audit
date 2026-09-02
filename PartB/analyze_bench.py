import csv

with open("bench/bench_log.csv", newline="") as f:
    rows = list(csv.DictReader(f))

print("LONG PROMPT THROUGHPUT ANALYSIS")
print("=" * 75)

for row in rows:

    prompt_len = int(row["prompt_len"])

    if prompt_len != 3584:
        continue

    batch = int(row["batch_size"])
    gen_len = int(row["gen_len"])
    wall_time = float(row["wall_clock_s"])

    # Actual generated tokens completed
    total_generated_tokens = batch * gen_len

    # Independent goodput calculation
    generated_tok_s = (
        total_generated_tokens / wall_time
    )

    reported = float(row["reported_tok_s"])

    print(
        f"\nBatch {batch}"
    )

    print(
        f"Generated tokens : "
        f"{total_generated_tokens}"
    )

    print(
        f"Wall clock       : "
        f"{wall_time:.2f} s"
    )

    print(
        f"Generated tok/s  : "
        f"{generated_tok_s:.2f}"
    )

    print(
        f"Reported tok/s   : "
        f"{reported:.2f}"
    )

    print(
        f"Preempted seqs   : "
        f"{row['preempted_seqs']}"
    )

    print(
        f"KV cache util    : "
        f"{row['kv_cache_util']}"
    )