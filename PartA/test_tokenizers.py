import tiktoken
from transformers import AutoTokenizer

text = "This is a tokenizer test."

# GPT-2
gpt2 = tiktoken.get_encoding("gpt2")
gpt2_tokens = gpt2.encode(text)

print("GPT-2 loaded")
print("Token count:", len(gpt2_tokens))

# Multilingual tokenizer
xlmr = AutoTokenizer.from_pretrained("xlm-roberta-base")
xlmr_tokens = xlmr.encode(text, add_special_tokens=False)

print("\nXLM-RoBERTa loaded")
print("Token count:", len(xlmr_tokens))