from agents import trace, Runner
from agentCollection.searchExecutionAgent import searchExecutionAgent
from agentCollection.todoAgent import QueryResponse
from agentCollection.todoAgent import todoAgent
from rich.console import Console
from rich.panel import Panel
from typing import List
# Web search tool
from langchain_community.tools.tavily_search import TavilySearchResults
from tavily import TavilyClient
# from duckduckgo_search import DDGS
from utils import _set_env
from dotenv import load_dotenv
import os

load_dotenv()
_set_env("TAVILY_API_KEY")

console = Console()


class ResearchAnalyst:
    def  __init__(self, query: str):
        self.query = query
    
    async def research_func(self) -> str:
        with trace("Deep Research Tool"):
            todos = await self.generateTodos() 
        return "dummy report"
    
    async def generateTodos(self) -> QueryResponse:
        result = await Runner.run(todoAgent, input=self.query)
        
        console.print(Panel(f"[bold cyan]ToDo Analysis[/bold cyan]"))
        console.print(f"[yellow]Thoughts:[/yellow] {result.final_output.thoughts}")
        console.print(f"[yellow]Generated ToDos:[/yellow] {result.final_output.queries}\n")
        
        for i, query in enumerate(result.final_output.queries, 1):
            console.print(f"[green]Query {i}:[/green] {query}")
            
        return result.final_output
    
    # def duckduckgo_search(query: str):
    #     try: 
    #         results = DDGS().text(query, region= "us-en", safesearch="on", timelimit="y", max_results= 1)
    #         return results
    #     except Exception as e:
    #         console.print(f"[bold orange]Error during search: {e}[/bold orange]")
    #         return []
    
    # we will use tavily for web search
    def search_tavily(query: str):
        
        # intiialize Tavily client
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            raise "Error: Tavily API key not found. Please set the TAVILY_API_KEY environment variable."
    
        tavily_client = TavilyClient(api_key=tavily_api_key)
        
        try:
            # call the tavily api using the client
            response = tavily_client.search(
                api_key=tavily_api_key,
                search_depth= "basic",
                max_results=1
            )
            
            if not response or "results" not in response:
                return f"No results found for query: {query}"
            
            #format the results
            results = response["results"].get('url', 'No URL')
                
            return results
        
        except Exception as e:
            return f"Error during Tavily search: {str(e)}"
            
            
    
    async def perform_research_for_todos(self, todos: List[str]):
        # get all of the the search results for each query
        
        all_search_results = {}
        for todo in todos.queries:
            search_results = self.search_tavily(todo)
            all_search_results[todo] = search_results
            
        for todo in todos:
            console.print(f"\n[bold green] Searching for: [/bold green] {todo}")
            
            for result in all_search_results[todo]:
                agent_result = await Runner.run(searchExecutionAgent, input=result)
            