import os
import ast

class CodeParser:
    def list_python_files(self, folder):
        py_files = []
        for root, _, files in os.walk(folder):
            for f in files:
                if f.endswith(".py") and "ath" not in root and ".aibuddy" not in root:
                    py_files.append(os.path.join(root, f))
        return py_files

    def read_file(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def extract_functions(self, code):
        tree = ast.parse(code)
        funcs = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        return funcs
