from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(["def foo(): pass", "print('hello')"])
from gpt4all import GPT4All

model = GPT4All("ggml-gpt4all-j-v1.bin")
response = model.generate("Explain this function: def foo(): pass")
print(response)
