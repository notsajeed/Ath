import os
import requests
from rich.console import Console
from .manager import load_config, get_api_key, set_config_value

console = Console()


class ChatAI:
    """Interactive AI chat assistant using config-managed providers"""

    def __init__(self):
        self.config = load_config()
        self.provider = self.config.get("provider", "ollama")
        self.model = self.config.get("model", "codellama:7b")
        self.conversation_history = []

    def set_provider(self, provider: str):
        """Set AI provider dynamically"""
        if provider.lower() not in ["openai", "anthropic", "ollama"]:
            console.print("[red]Invalid provider. Choose openai, anthropic, or ollama.[/red]")
            return False
        self.provider = provider.lower()
        set_config_value("provider", self.provider)
        console.print(f"[green]Provider set to {self.provider}[/green]")
        return True

    def set_model(self, model: str):
        """Set AI model dynamically"""
        self.model = model
        set_config_value("model", self.model)
        console.print(f"[green]Model set to {self.model}[/green]")

    def _get_system_prompt(self):
        """Basic system prompt"""
        return (
            f"You are Ath AI assistant using {self.provider} ({self.model}).\n"
            "Answer questions about Python codebases. Be concise and clear."
        )

    def _get_openai_response(self, question: str) -> str:
        try:
            import openai
        except ImportError:
            return "OpenAI library not installed. Run: pip install openai"

        api_key = get_api_key("openai")
        if not api_key:
            return "OpenAI API key not set. Use 'ath config set openai_key <key>'"

        openai.api_key = api_key
        try:
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": question}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            return f"OpenAI API error: {e}"

    def _get_anthropic_response(self, question: str) -> str:
        try:
            import anthropic
        except ImportError:
            return "Anthropic library not installed. Run: pip install anthropic"

        api_key = get_api_key("anthropic")
        if not api_key:
            return "Anthropic API key not set. Use 'ath config set anthropic_key <key>'"

        client = anthropic.Client(api_key=api_key)
        prompt = f"{self._get_system_prompt()}\n\nUser: {question}\nAssistant:"
        try:
            msg = client.completions.create(
                model=self.model,
                prompt=prompt,
                max_tokens_to_sample=500
            )
            return msg.completion
        except Exception as e:
            return f"Anthropic API error: {e}"

    def _get_ollama_response(self, question: str) -> str:
        """Send request to local Ollama"""
        try:
            system_prompt = self._get_system_prompt()
            payload = {
                "model": self.model,
                "prompt": f"{system_prompt}\n\nUser: {question}",
                "stream": False
            }
            r = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
            if r.status_code == 200:
                return r.json().get("response", "No response from Ollama")
            else:
                return f"Ollama API error: {r.status_code}"
        except requests.exceptions.ConnectionError:
            return "Cannot connect to Ollama. Make sure it's running: ollama serve"
        except Exception as e:
            return f"Ollama error: {e}"

    def ask(self, question: str) -> str:
        """Ask a question to the selected provider"""
        self.conversation_history.append({"question": question})
        if self.provider == "openai":
            resp = self._get_openai_response(question)
        elif self.provider == "anthropic":
            resp = self._get_anthropic_response(question)
        elif self.provider == "ollama":
            resp = self._get_ollama_response(question)
        else:
            resp = f"Unknown provider: {self.provider}"
        self.conversation_history[-1]["response"] = resp
        return resp

    def start_interactive_chat(self):
        """Interactive console chat"""
        console.print(f"[blue]Ath AI Chat activated using {self.provider} ({self.model})[/blue]")
        console.print("[dim]Type 'exit', 'quit', or 'q' to stop.[/dim]\n")
        while True:
            try:
                question = input("You: ").strip()
                if question.lower() in ["exit", "quit", "q"]:
                    break
                if not question:
                    continue
                with console.status("[dim]Thinking...[/dim]"):
                    answer = self.ask(question)
                console.print(f"[green]Ath:[/green] {answer}\n")
            except KeyboardInterrupt:
                break
            except EOFError:
                break
        console.print("[blue]Chat ended.[/blue]")
