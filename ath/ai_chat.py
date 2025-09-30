"""
AI Chat module for Ath - handles AI interaction logic
Clean version focused on real AI providers only
"""

import os
import requests
from typing import List, Dict, Any
from pathlib import Path
from rich.console import Console

console = Console()

class AthAI:
    """AI assistant for code understanding - real AI providers only"""
    def __init__(self, storage, ai_provider):
        self.storage = storage
        self.ai_provider = ai_provider
        self.conversation_history = []
        self.project_context = None
        
    def initialize(self):
        """Initialize the AI with project context"""
        try:
            code_chunks = self.storage.get_all_chunks()
            self.project_context = self._build_project_context(code_chunks)
            console.print(f"[dim]Loaded {len(code_chunks)} code chunks for AI context[/dim]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to initialize AI: {e}[/red]")
            return False
    
    def chat(self, question: str) -> str:
        """Main chat interface - returns AI response"""
        try:
            # Find relevant code chunks for this question
            relevant_chunks = self._find_relevant_chunks(question)
            
            # Get AI response
            response = self._get_ai_response(question, relevant_chunks)
            
            # Store in conversation history
            self.conversation_history.append({
                "question": question,
                "response": response,
                "relevant_chunks": [chunk.get('id', 'unknown') for chunk in relevant_chunks]
            })
            
            return response
            
        except Exception as e:
            return f"Sorry, I encountered an error: {e}"
    
    def _build_project_context(self, code_chunks: List[Dict]) -> str:
        """Build comprehensive project context from code chunks"""
        context_parts = ["=== PROJECT OVERVIEW ==="]
        
        # Group by file for better organization
        files = {}
        for chunk in code_chunks:
            file_path = chunk.get('file_path', 'unknown')
            if file_path not in files:
                files[file_path] = []
            files[file_path].append(chunk)
        
        context_parts.append(f"Total files: {len(files)}")
        context_parts.append(f"Total code chunks: {len(code_chunks)}")
        
        # Add file structure overview
        context_parts.append("\n=== FILE STRUCTURE ===")
        for file_path, chunks in files.items():
            functions = [c for c in chunks if c.get('chunk_type') == 'function']
            classes = [c for c in chunks if c.get('chunk_type') == 'class']
            
            context_parts.append(f"\n{file_path}:")
            if classes:
                context_parts.append(f"  Classes: {', '.join(c['name'] for c in classes)}")
            if functions:
                context_parts.append(f"  Functions: {', '.join(f['name'] for f in functions)}")
        
        return "\n".join(context_parts)
    
    def _find_relevant_chunks(self, question: str) -> List[Dict]:
        """Find code chunks most relevant to the question"""
        try:
            all_chunks = self.storage.get_all_chunks()
            relevant = []
            question_words = set(word.lower() for word in question.split() if len(word) > 2)
            
            for chunk in all_chunks:
                score = 0
                
                # Score based on name matches
                name = chunk.get('name', '').lower()
                name_words = set(name.split('_') + name.split())
                score += len(question_words & name_words) * 5
                
                # Score based on docstring matches
                docstring = chunk.get('docstring', '').lower()
                if docstring:
                    docstring_words = set(docstring.split())
                    score += len(question_words & docstring_words) * 3
                
                # Score based on file path matches
                file_path = chunk.get('file_path', '').lower()
                file_words = set(file_path.replace('/', ' ').replace('.', ' ').split())
                score += len(question_words & file_words) * 2
                
                if score > 0:
                    relevant.append((chunk, score))
            
            # Sort by relevance and return top chunks
            relevant.sort(key=lambda x: x[1], reverse=True)
            return [chunk for chunk, score in relevant[:5]]
            
        except Exception as e:
            console.print(f"[yellow]Warning: Could not find relevant chunks: {e}[/yellow]")
            return []
    
    def _get_ai_response(self, question: str, relevant_chunks: List[Dict]) -> str:
        """Get response from AI provider"""
        if self.ai_provider == "openai":
            return self._get_openai_response(question, relevant_chunks)
        elif self.ai_provider == "anthropic":
            return self._get_anthropic_response(question, relevant_chunks)
        elif self.ai_provider == "ollama":
            return self._get_ollama_response(question, relevant_chunks)
        else:
            return f"Unknown AI provider: {self.ai_provider}"
    
    def _get_openai_response(self, question: str, relevant_chunks: List[Dict]) -> str:
        """Get response from OpenAI"""
        try:
            import openai
            
            if not os.getenv('OPENAI_API_KEY'):
                return "Please set your OPENAI_API_KEY environment variable to use OpenAI."
            
            openai.api_key = os.getenv('OPENAI_API_KEY')
            
            system_prompt = self._build_system_prompt(relevant_chunks)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except ImportError:
            return "OpenAI library not installed. Run: pip install openai"
        except Exception as e:
            return f"OpenAI API error: {e}"
    
    def _get_anthropic_response(self, question: str, relevant_chunks: List[Dict]) -> str:
        """Get response from Anthropic Claude"""
        try:
            import anthropic
            
            if not os.getenv('ANTHROPIC_API_KEY'):
                return "Please set your ANTHROPIC_API_KEY environment variable to use Anthropic."
            
            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            
            system_prompt = self._build_system_prompt(relevant_chunks)
            
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": question}
                ]
            )
            
            return message.content[0].text
            
        except ImportError:
            return "Anthropic library not installed. Run: pip install anthropic"
        except Exception as e:
            return f"Anthropic API error: {e}"
    
    def _get_ollama_response(self, question: str, relevant_chunks: List[Dict]) -> str:
        """Get response from local Ollama"""
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code != 200:
                return "Ollama is not running. Start it with: ollama serve"
            
            # Build prompt with context
            system_prompt = self._build_system_prompt(relevant_chunks)
            full_prompt = f"{system_prompt}\n\nUser question: {question}"
            
            # Send to Ollama
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma3:1b", #CHANGE THE MODEL HERE
                    "prompt": full_prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "No response from Ollama")
            else:
                return f"Ollama error: {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return "Cannot connect to Ollama. Make sure it's running: ollama serve"
        except requests.exceptions.Timeout:
            return "Ollama request timed out. The model might be loading."
        except Exception as e:
            return f"Ollama error: {e}"
    
    def _build_system_prompt(self, relevant_chunks: List[Dict]) -> str:
        """Build system prompt with project context"""
        prompt_parts = [
            "You are Ath, an AI assistant that helps developers understand and work with their specific codebase.",
            "You have access to the complete source code and can provide detailed, contextual help.",
            "",
            "PROJECT CONTEXT:",
            self.project_context[:1500] if self.project_context else "No context available",
        ]
        
        if relevant_chunks:
            prompt_parts.append("\nRELEVANT CODE SECTIONS:")
            for chunk in relevant_chunks:
                name = chunk.get('name', 'unknown')
                chunk_type = chunk.get('chunk_type', 'unknown')
                file_path = chunk.get('file_path', 'unknown')
                docstring = chunk.get('docstring', '')
                
                prompt_parts.append(f"\n{chunk_type.upper()}: {name} in {file_path}")
                if docstring:
                    prompt_parts.append(f"Documentation: {docstring}")
        
        prompt_parts.extend([
            "",
            "Guidelines:",
            "- Reference specific functions, classes, and files from this codebase",
            "- Provide practical examples using the actual project structure", 
            "- Help with debugging by understanding the full context",
            "- Suggest improvements based on existing patterns",
            "- Be specific about line numbers and file locations when helpful",
            "- Keep responses concise but informative"
        ])
        
        return "\n".join(prompt_parts)

def start_interactive_chat(storage, ai_provider):
    """Start interactive chat session"""
    # Validate provider
    valid_providers = ["openai", "anthropic", "ollama"]
    if ai_provider not in valid_providers:
        console.print(f"[red]Please choose an AI provider:[/red]")
        console.print("  [green]--provider ollama[/green]     (free, local)")
        console.print("  [green]--provider openai[/green]     (paid, cloud)")
        console.print("  [green]--provider anthropic[/green] (paid, cloud)")
        console.print("\n[dim]Use 'ath inspect <file>' to browse your code structure[/dim]")
        return False
    
    ai = AthAI(storage, ai_provider)
    
    if not ai.initialize():
        return False
    
    console.print(f"[blue]Chat mode activated with {ai_provider}. Type 'exit', 'quit', or 'q' to quit.[/blue]")
    console.print("[dim]Ask me anything about your codebase![/dim]\n")
    
    while True:
        try:
            question = input("You: ").strip()
            if question.lower() in ['exit', 'quit', 'q']:
                break
            
            if not question:
                continue
                
            with console.status("[dim]Thinking...[/dim]"):
                response = ai.chat(question)
            
            console.print(f"[green]Ath:[/green] {response}\n")
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    console.print("[blue]Chat ended.[/blue]")
    return True