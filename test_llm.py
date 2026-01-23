from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    device_map="cpu"
)

pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=300,
    do_sample=False,
    eos_token_id=tokenizer.eos_token_id
)

prompt = """
<|system|>
You are an information extraction engine.
Return ONLY valid JSON. No explanations.
</|system|>

<|user|>
Extract projects from the text below.

Return format:
[
  {
    "title": "",
    "description": []
  }
]

Text:
Project: Resume to Portfolio
- Built a system using FastAPI and LLMs
- Automatically generates portfolios
- Integrated with GitLab
</|user|>

<|assistant|>
"""

out = pipe(prompt)
print(out[0]["generated_text"])
