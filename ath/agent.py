import os
from ath.parser import CodeParser
from ath.embeddings import EmbeddingDB
from ath.llm_interface import LLMInterface
import json

AIBUDDY_DIR = ".aibuddy"

class ProjectAgent:
    def __init__(self):
        os.makedirs(AIBUDDY_DIR, exist_ok=True)
        self.parser = CodeParser()
        self.db = EmbeddingDB(f"{AIBUDDY_DIR}/embeddings.db")
        self.llm = LLMInterface()
        self.chat_history_file = f"{AIBUDDY_DIR}/chat_history.json"
        if not os.path.exists(self.chat_history_file):
            with open(self.chat_history_file, "w") as f:
                json.dump([], f)

    def initialize(self):
        print("Scanning project files...")
        files = self.parser.list_python_files(".")
        for file in files:
            content = self.parser.read_file(file)
            self.db.add_document(file, content)
        self.db.save()
        print("Initialization complete!")

    def explain_file(self, file_path):
        code = self.parser.read_file(file_path)
        return self.llm.explain_code(code)

    def annotate_file(self, file_path):
        code = self.parser.read_file(file_path)
        annotated = self.llm.annotate_code(code)
        with open(file_path, "w") as f:
            f.write(annotated)
        print(f"Annotated {file_path}")

    def search(self, query):
        results = self.db.semantic_search(query)
        return results

    def chat_interactive(self):
        with open(self.chat_history_file, "r") as f:
            history = json.load(f)
        while True:
            query = input("You: ")
            if query.lower() in ["exit", "quit"]:
                break
            answer = self.llm.answer_query(query, context=history)
            print(f"Ath: {answer}")
            history.append({"query": query, "answer": answer})
        with open(self.chat_history_file, "w") as f:
            json.dump(history, f)
