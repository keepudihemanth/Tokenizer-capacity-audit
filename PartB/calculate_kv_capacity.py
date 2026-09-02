# Model specification
layers = 28
kv_heads = 8
head_dim = 128

# FP16
bytes_per_value = 2

# K and V
kv_multiplier = 2


# GPU configuration
gpu_memory_gb = 24
gpu_memory_utilization = 0.92
runtime_overhead_gb = 1.6

# Sequence length
sequence_length = 4096


# 1. KV-cache bytes per token

kv_bytes_per_token = (
    layers
    * kv_heads
    * head_dim
    * kv_multiplier
    * bytes_per_value
)

print("KV CACHE CAPACITY CALCULATION")
print("=" * 50)

print("\n1. KV-cache per token")

print(
    f"{layers} layers × "
    f"{kv_heads} KV heads × "
    f"{head_dim} head_dim × "
    f"{kv_multiplier} (K+V) × "
    f"{bytes_per_value} bytes"
)

print(f"= {kv_bytes_per_token:,} bytes/token")

print(
    f"= {kv_bytes_per_token / 1024:.2f} KiB/token"
)


# 2. Available memory

usable_memory_gb = (
    gpu_memory_gb
    * gpu_memory_utilization
)

kv_memory_gb = (
    usable_memory_gb
    - runtime_overhead_gb
)

print("\n2. Memory available for KV cache")

print(
    f"Usable GPU memory = "
    f"{gpu_memory_gb} GB × "
    f"{gpu_memory_utilization}"
)

print(f"= {usable_memory_gb:.2f} GB")

print(
    f"\nKV memory budget = "
    f"{usable_memory_gb:.2f} GB - "
    f"{runtime_overhead_gb} GB"
)

print(f"= {kv_memory_gb:.2f} GB")


# 3. KV memory per sequence

kv_bytes_per_sequence = (
    sequence_length
    * kv_bytes_per_token
)

print("\n3. KV-cache per 4096-token sequence")

print(
    f"{sequence_length} tokens × "
    f"{kv_bytes_per_token:,} bytes"
)

print(
    f"= {kv_bytes_per_sequence:,} bytes"
)

print(
    f"= {kv_bytes_per_sequence / (1024 ** 3):.4f} GiB"
)


# 4. Maximum concurrent sequences

# Use GiB consistently with byte calculation
usable_memory_bytes = (
    gpu_memory_gb
    * (1024 ** 3)
    * gpu_memory_utilization
)

runtime_overhead_bytes = (
    runtime_overhead_gb
    * (1024 ** 3)
)

kv_memory_bytes = (
    usable_memory_bytes
    - runtime_overhead_bytes
)

max_sequences = (
    kv_memory_bytes
    // kv_bytes_per_sequence
)

print("\n4. Maximum concurrent 4096-token sequences")

print(
    f"KV memory budget = "
    f"{kv_memory_bytes:,} bytes"
)

print(
    f"Sequence KV memory = "
    f"{kv_bytes_per_sequence:,} bytes"
)

print(
    f"\nMaximum whole sequences = "
    f"{int(max_sequences)}"
)