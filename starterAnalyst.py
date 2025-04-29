from agents import trace, Runner
from agentCollection.todoAgent import QueryResponse
from agentCollection import todoAgent
from rich.console import Console
from rich.panel import Panel


console = Console()

class ResearchAnalyst:
    def  __init__(self, query: str):
        self.query = query
    
    async def research(self) -> str:
        with trace("Deep Research Tool"):
    
    async def generateTodos(self) -> QueryResponse:
        result = await Runner.run(todoAgent, input=self.query)
        
        console.print(Panel(f"[bold cyan]ToDo Analysis[/bold cyan]"))
        console.print(f"[yellow]Thoughts:[/yellow] {result.final_output.thoughts}")
        console.print(f"[yellow]Generated ToDos:[/yellow] {result.final_output.queries}")
        
        for i, query in enumerate(result.final_output.queries, 1):
            console.print(f"[green]Query {i}:[/green] {query}")
            
        return result.final_output