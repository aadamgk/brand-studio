# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Status

Greenfield project — no code exists yet. The repo currently contains only the assignment brief (`IA-YNOV-ProjetIAGen.pdf`). When implementation starts, update this file with real build/run/test commands and architecture notes.

## Project goal

Individual graded project for the YNOV "Mastère Data Scientist" Deep Learning course (instructor: Antoine Vacavant). The objective is to **build a simple interface to interact with a generative AI / language model**. Topic is open — text, image, or audio generation are all acceptable.

## Constraints from the brief

- Load a generative model from **Hugging Face** (`transformers`) or **NVIDIA NIM / NGC** (OpenAI-compatible API via the `openai` package, requires an API key).
- Build a user-facing interface to exchange with the model. **Streamlit** is the suggested framework.
- Host the final product if possible.
- Required deliverables: Python source code, hosting link (if any), a README listing the technologies used, and **demo videos**.

## Reference snippets from the brief

Hugging Face `transformers`:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained('roneneldan/TinyStories-1M')
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neo-125M")
input_ids = tokenizer.encode(prompt, return_tensors="pt")
output = model.generate(input_ids, max_length=1000, num_beams=1)
print(tokenizer.decode(output[0], skip_special_tokens=True))
```

NVIDIA NIM (OpenAI-compatible):
```python
from openai import OpenAI
client = OpenAI(base_url="https://integrate.api.nvidia.com/v1", api_key="YOUR_API_KEY")
completion = client.chat.completions.create(
    model="meta/llama3-70b-instruct",
    messages=[{"role": "user", "content": "..."}],
    temperature=0.5, top_p=0.7, max_tokens=1024, stream=True,
)
```

The NVIDIA API key must be kept out of source control (use an env var or a `.env` file ignored by git).
