import typer
from ath.agent import ProjectAgent

app = typer.Typer()
agent = ProjectAgent()

@app.command()
def init():
    """Initialize project AI agent"""
    agent.initialize()

@app.command()
def explain(file: str):
    """Explain code in a file"""
    print(agent.explain_file(file))

@app.command()
def annotate(file: str):
    """Add docstrings to functions/classes"""
    agent.annotate_file(file)

@app.command()
def search(query: str):
    """Semantic search across project"""
    results = agent.search(query)
    for r in results:
        print(r)

@app.command()
def chat():
    """Interactive project Q&A"""
    agent.chat_interactive()

if __name__ == "__main__":
    app()
