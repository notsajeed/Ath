import typer
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress
from .scanner import ProjectScanner
from .storage import LocalStorage
from .utils import find_project_root, find_aibuddy_dir
from .utils import get_project_stats
from .ai_chat import ChatAI

app = typer.Typer(help="Ath - Your personal, per-folder AI assistant")
console = Console()


@app.command()
def init(force: bool = typer.Option(False, "--force", "-f", help="Force re-initialization")):
    """Initialize AI agent for current project"""
    project_root = find_project_root()
    aibuddy_dir = project_root / ".aibuddy"

    if project_root != Path.cwd():
        console.print(f"[blue]Found project root at: {project_root}[/blue]")

    if aibuddy_dir.exists() and not force:
        console.print("[yellow]Project already initialized! Use --force to re-initialize.[/yellow]")
        console.print(f"[dim]Location: {aibuddy_dir}[/dim]")
        return

    console.print(f"[green]Initializing Ath agent in {project_root.name}[/green]")

    if force and aibuddy_dir.exists():
        shutil.rmtree(aibuddy_dir)
        console.print("✓ Cleaned existing data")

    aibuddy_dir.mkdir(exist_ok=True)
    console.print("✓ Created .aibuddy directory")

    storage = LocalStorage(aibuddy_dir)
    storage.init_db()
    console.print("✓ Initialized database")

    scanner = ProjectScanner(project_root)
    with Progress() as progress:
        task = progress.add_task("Scanning project files...", total=None)
        code_chunks = scanner.scan_project()
        progress.update(task, completed=100, total=100)

    storage.store_code_chunks(code_chunks)
    console.print(f"✓ Processed {len(code_chunks)} code chunks")
    console.print("[bold green]Project initialized successfully![/bold green]")


@app.command()
def status():
    """Show project status and statistics"""
    aibuddy_dir = find_aibuddy_dir()
    if not aibuddy_dir:
        console.print("[red]No AI agent found. Run 'ath init' first.[/red]")
        return

    if aibuddy_dir.parent != Path.cwd():
        console.print(f"[dim]Using project at: {aibuddy_dir.parent}[/dim]")

    try:
        stats = get_project_stats(aibuddy_dir)
        console.print(f"[green]Project Status:[/green]")
        console.print(f"  Files scanned: {stats['files']}")
        console.print(f"  Total chunks: {stats['total_chunks']}")
        console.print(f"  Functions: {stats['functions']}")
        console.print(f"  Classes: {stats['classes']}")

        db_path = aibuddy_dir / "data.db"
        if db_path.exists():
            size_kb = db_path.stat().st_size / 1024
            console.print(f"  Database size: {size_kb:.1f} KB")
    except Exception as e:
        console.print(f"[red]Error reading project data: {e}[/red]")
        console.print("[yellow]Try running 'ath init --force' to reinitialize.[/yellow]")


@app.command()
def chat(provider: str = typer.Option(None, "--provider", "-p", help="AI provider: openai, anthropic, ollama")):
    """Start interactive chat with project AI"""
    aibuddy_dir = find_aibuddy_dir()
    if not aibuddy_dir:
        console.print("[red]No AI agent found. Run 'ath init' first.[/red]")
        return

    if aibuddy_dir.parent != Path.cwd():
        console.print(f"[dim]Using project at: {aibuddy_dir.parent}[/dim]")

    storage = LocalStorage(aibuddy_dir)
    try:
        code_chunks = storage.get_all_chunks()
        if not code_chunks:
            console.print("[yellow]No code chunks found. Run 'ath init' to scan your project.[/yellow]")
            return
    except Exception as e:
        console.print(f"[red]Database error: {e}[/red]")
        console.print("[yellow]Try running 'ath init --force' to fix the database.[/yellow]")
        return

    chat_ai = ChatAI()
    if provider:
        chat_ai.set_provider(provider)
    chat_ai.start_interactive_chat()


@app.command()
def inspect(file_path: str = typer.Argument(help="File to inspect")):
    """Show what code chunks were extracted from a file"""
    aibuddy_dir = find_aibuddy_dir()
    if not aibuddy_dir:
        console.print("[red]No AI agent found. Run 'ath init' first.[/red]")
        return

    if aibuddy_dir.parent != Path.cwd():
        console.print(f"[dim]Using project at: {aibuddy_dir.parent}[/dim]")

    storage = LocalStorage(aibuddy_dir)
    chunks = storage.get_chunks_by_file(file_path)
    if not chunks:
        console.print(f"[yellow]No chunks found for file: {file_path}[/yellow]")
        return

    console.print(f"[green]Code chunks in {file_path}:[/green]")
    for chunk in chunks:
        console.print(f"  {chunk['chunk_type']}: {chunk['name']} (lines {chunk['line_start']}-{chunk['line_end']})")
        if chunk['docstring']:
            console.print(f"    Doc: {chunk['docstring'][:100]}...")

@app.command()
def config(
    action: str = typer.Argument(..., help="Action: show, set, get"),
    key: str = typer.Argument(None, help="Config key (for set/get)"),
    value: str = typer.Argument(None, help="Value (for set)")
):
    """Manage Ath configuration (API keys, provider, model)"""
    from .manager import show_config, set_config_value, get_config_value

    if action == "show":
        show_config()
    elif action == "set":
        if not key or not value:
            console.print("[red]You must provide key and value to set.[/red]")
            return
        set_config_value(key, value)
        console.print(f"[green]Set {key} to {value}[/green]")
    elif action == "get":
        if not key:
            console.print("[red]You must provide key to get.[/red]")
            return
        val = get_config_value(key)
        console.print(f"[green]{key} = {val}[/green]")
    else:
        console.print("[red]Unknown config action. Use show, set, or get.[/red]")

if __name__ == "__main__":
    app()
