# ath/cli.py - Fixed version with all commands
import typer
import shutil
from pathlib import Path
from rich.console import Console
from rich.progress import Progress
from .scanner import ProjectScanner
from .storage import LocalStorage

app = typer.Typer(help="Ath - Your personal, per-folder AI assistant")
console = Console()

@app.command()
def init(force: bool = typer.Option(False, "--force", "-f", help="Force re-initialization")):
    """Initialize AI agent for current project"""
    current_dir = Path.cwd()
    aibuddy_dir = current_dir / ".aibuddy"
    
    # Check if already initialized
    if aibuddy_dir.exists() and not force:
        console.print("[yellow]Project already initialized! Use --force to re-initialize.[/yellow]")
        return
    
    console.print(f"[green]Initializing Ath agent in {current_dir.name}[/green]")
    
    # Create .aibuddy directory (remove if force)
    if force and aibuddy_dir.exists():
        shutil.rmtree(aibuddy_dir)
        console.print("✓ Cleaned existing data")
    
    aibuddy_dir.mkdir(exist_ok=True)
    console.print("✓ Created .aibuddy directory")
    
    # Initialize storage
    storage = LocalStorage(aibuddy_dir)
    storage.init_db()
    console.print("✓ Initialized database")
    
    # Scan project
    scanner = ProjectScanner(current_dir)
    
    with Progress() as progress:
        task = progress.add_task("Scanning project files...", total=None)
        code_chunks = scanner.scan_project()
        progress.update(task, completed=100, total=100)
    
    # Store results
    storage.store_code_chunks(code_chunks)
    console.print(f"✓ Processed {len(code_chunks)} code chunks")
    
    console.print("[bold green]Project initialized successfully![/bold green]")

@app.command()
def status():
    """Show project status and statistics"""
    aibuddy_dir = Path.cwd() / ".aibuddy"
    
    if not aibuddy_dir.exists():
        console.print("[red]No AI agent found. Run 'ath init' first.[/red]")
        return
    
    from .utils import get_project_stats
    
    try:
        stats = get_project_stats(aibuddy_dir)
        console.print(f"[green]Project Status:[/green]")
        console.print(f"  Files scanned: {stats['files']}")
        console.print(f"  Total chunks: {stats['total_chunks']}")
        console.print(f"  Functions: {stats['functions']}")
        console.print(f"  Classes: {stats['classes']}")
        
        # Show database file info
        db_path = aibuddy_dir / "data.db"
        if db_path.exists():
            size_kb = db_path.stat().st_size / 1024
            console.print(f"  Database size: {size_kb:.1f} KB")
        
    except Exception as e:
        console.print(f"[red]Error reading project data: {e}[/red]")
        console.print("[yellow]Try running 'ath init --force' to reinitialize.[/yellow]")

@app.command()
def chat():
    """Start interactive chat with project AI"""
    aibuddy_dir = Path.cwd() / ".aibuddy"
    
    if not aibuddy_dir.exists():
        console.print("[red]No AI agent found. Run 'ath init' first.[/red]")
        return
    
    console.print("[blue]Chat mode activated. Type 'exit' to quit.[/blue]")
    
    storage = LocalStorage(aibuddy_dir)
    
    # Test database connection first
    try:
        code_chunks = storage.get_all_chunks()
    except Exception as e:
        console.print(f"[red]Database error: {e}[/red]")
        console.print("[yellow]Try running 'ath init --force' to fix the database.[/yellow]")
        return
    
    while True:
        try:
            question = typer.prompt("You")
            if question.lower() in ['exit', 'quit', 'q']:
                break
            
            # For now, just echo back with stored code context
            response = f"I found {len(code_chunks)} code chunks in your project. You asked: '{question}'"
            console.print(f"[green]Ath:[/green] {response}")
            
        except KeyboardInterrupt:
            break
    
    console.print("[blue]Chat ended.[/blue]")

@app.command()
def inspect(file_path: str = typer.Argument(help="File to inspect")):
    """Show what code chunks were extracted from a file"""
    aibuddy_dir = Path.cwd() / ".aibuddy"
    
    if not aibuddy_dir.exists():
        console.print("[red]No AI agent found. Run 'ath init' first.[/red]")
        return
    
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

if __name__ == "__main__":
    app()