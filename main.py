from dotenv import load_dotenv
import os
from rich.console import Console
from rich.prompt import Prompt
import asyncio 
from starterAnalyst import ResearchAnalyst

# load the environment variables from the .env file
load_dotenv()

console = Console()

async def main() -> None:
    """
    Main function to run the agent
    """
    console.print("[bold cyan]Deep Research tool for Karta[/bold cyan]")
    
    # get the user input
    query = Prompt.ask("\n[bold]What would you like to know about?[/bold]")
    
    if not query.strip():
        console.print("[bold red]Please provide a valid query.[/bold red]")
        return
    
    researchAnalyst = ResearchAnalyst(query)

    report = await researchAnalyst.research_func()
    
    print("\n[bold cyan]Research Report: \n[/bold cyan]")
    print(report)
    
    
    

if __name__ == "__main__":
    asyncio.run(main())