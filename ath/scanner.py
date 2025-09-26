import ast
import os
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

@dataclass
class CodeChunk:
    file_path: str
    chunk_type: str  # 'function', 'class', 'module'
    name: str
    content: str
    line_start: int
    line_end: int
    docstring: str = ""

class ProjectScanner:
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.ignore_patterns = {'.git', '__pycache__', '.aibuddy', 'node_modules', '.env'}
    
    def scan_project(self) -> List[CodeChunk]:
        """Scan project and extract code chunks"""
        chunks = []
        
        for py_file in self._find_python_files():
            file_chunks = self._parse_python_file(py_file)
            chunks.extend(file_chunks)
        
        return chunks
    
    def _find_python_files(self) -> List[Path]:
        """Find all Python files in project"""
        python_files = []
        
        for root, dirs, files in os.walk(self.project_path):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_patterns]
            
            for file in files:
                if file.endswith('.py'):
                    python_files.append(Path(root) / file)
        
        return python_files
    
    def _parse_python_file(self, file_path: Path) -> List[CodeChunk]:
        """Parse a Python file and extract functions/classes"""
        chunks = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Add module-level chunk
            relative_path = str(file_path.relative_to(self.project_path))
            module_chunk = CodeChunk(
                file_path=relative_path,
                chunk_type='module',
                name=file_path.stem,
                content=content[:500],  # First 500 chars
                line_start=1,
                line_end=len(content.split('\n')),
                docstring=ast.get_docstring(tree) or ""
            )
            chunks.append(module_chunk)
            
            # Extract functions and classes
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    chunk = self._extract_node_chunk(node, content, relative_path)
                    if chunk:
                        chunks.append(chunk)
        
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
        
        return chunks
    
    def _extract_node_chunk(self, node: ast.AST, file_content: str, file_path: str) -> CodeChunk:
        """Extract a function or class as a code chunk"""
        lines = file_content.split('\n')
        
        # Get the actual code content
        start_line = node.lineno - 1
        end_line = node.end_lineno if hasattr(node, 'end_lineno') else start_line + 10
        code_content = '\n'.join(lines[start_line:end_line])
        
        chunk_type = 'function' if isinstance(node, ast.FunctionDef) else 'class'
        
        return CodeChunk(
            file_path=file_path,
            chunk_type=chunk_type,
            name=node.name,
            content=code_content,
            line_start=node.lineno,
            line_end=end_line,
            docstring=ast.get_docstring(node) or ""
        )