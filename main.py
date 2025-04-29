from dotenv import load_dotenv
import os
from rich.console import Console
from rich.prompt import Prompt
import asyncio 

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

if __name__ == "__main__":
    asyncio.run(main())