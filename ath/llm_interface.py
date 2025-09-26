from gpt4all import GPT4All

class LLMInterface:
    def __init__(self):
        self.model = GPT4All("ggml-gpt4all-j-v1.bin")

    def explain_code(self, code):
        prompt = f"Explain this Python code in simple terms:\n\n{code}"
        return self.model.generate(prompt)

    def annotate_code(self, code):
        prompt = f"Add meaningful docstrings to all functions/classes:\n\n{code}"
        return self.model.generate(prompt)

    def answer_query(self, query, context=None):
        history_text = ""
        if context:
            for item in context[-5:]:
                history_text += f"Q: {item['query']}\nA: {item['answer']}\n"
        prompt = f"{history_text}\nQuestion: {query}\nAnswer:"
        return self.model.generate(prompt)
