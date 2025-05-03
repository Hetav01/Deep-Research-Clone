from agents import trace, Runner
from agentCollection.searchExecutionAgent import searchExecutionAgent
from agentCollection.todoAgent import QueryResponse
from agentCollection.todoAgent import todoAgent
from pydanticModels import SearchExecutionResponse

from rich.console import Console
from rich.panel import Panel
from typing import List
from utils import _set_env, save_report_as_markdown
from dotenv import load_dotenv
import os
import json
import time

# Web search tools
from langchain_community.tools.tavily_search import TavilySearchResults
from tavily import TavilyClient
from duckduckgo_search import DDGS


load_dotenv()
_set_env("TAVILY_API_KEY")

console = Console()


class ResearchAnalyst:
    def  __init__(self, query: str):
        self.query = query
        self.search_responses = []
    
    async def research_func(self) -> str:
        with trace("Deep Research Tool"):
            todos = await self.generateTodos() 
            
            await self.perform_research_for_todos(todos.queries)
            
            deepresearch_report = await self.deepresearch_final_report()
            
            # Save the report as a PDF
            # output_pdf_path = save_report_as_pdf(deepresearch_report, "output/deep_research_report.pdf")
            # console.print(f"[green]Report saved as PDF at: {output_pdf_path}[/green]")
            # Save the report as a Markdown file
            output_md_path = save_report_as_markdown(deepresearch_report, "output/deep_research_report.md")
            console.print(f"[green]Report saved as Markdown at: {output_md_path}[/green]")
            
        return deepresearch_report
    
    async def generateTodos(self) -> QueryResponse:
        result = await Runner.run(todoAgent, input=self.query)
        
        console.print(Panel(f"[bold cyan]ToDo Analysis[/bold cyan]"))
        console.print(f"[yellow]Thoughts:[/yellow] {result.final_output.thoughts}")
        console.print(f"[yellow]Generated ToDos:[/yellow] {result.final_output.queries}\n")
        
        for i, query in enumerate(result.final_output.queries, 1):
            console.print(f"[green]Query {i}:[/green] {query}")
            
        return result.final_output
    
    def duckduckgo_search(query: str):
        try: 
            results = DDGS().text(query, region= "us-en", safesearch="on", timelimit="y", max_results= 1)
            return results
        except Exception as e:
            console.print(f"[bold orange]Error during search: {e}[/bold orange]")
            return []
    
    # we will use tavily for web search
    def search_tavily(self, query: str):
        
        # intiialize Tavily client
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            raise "Error: Tavily API key not found. Please set the TAVILY_API_KEY environment variable."
    
        tavily_client = TavilyClient(api_key=tavily_api_key)
        
        # try:
        #     # call the tavily api using the client
        #     response = tavily_client.search(
        #         api_key=tavily_api_key,
        #         search_depth= "basic",
        #         max_results=1
        #     )
            
        #     if not response or "results" not in response:
        #         return f"No results found for query: {query}"
            
        #     #format the results
        #     results = response["results"]
                
        #     return results
        
        # except Exception as e:
        #     return f"Error during Tavily search: {str(e)}"
        try:
            response = tavily_client.search(
                query=query,
                api_key=tavily_api_key,
                search_depth="basic",
                max_results=5
            )
            
            # Debugging: Print the response
            console.print(f"[green]Response from Tavily for query '{query}':[/green] {response}")

            # Extract results
            results = response.get("results", [])
            if not isinstance(results, list):
                console.print("[red]Error: 'results' is not a list![/red]")
                return []

            # Return the results
            return results
        except Exception as e:
            console.print(f"[bold orange]Error during Tavily search: {e}[/bold orange]")
            return []
                
            
    
    async def perform_research_for_todos(self, todos: List[str]):
        # get all of the the search results for each query
        
        all_search_results = {}
        for todo in todos:
            search_results = self.search_tavily(todo)
            all_search_results[todo] = search_results
            
        for todo in todos:
            console.print(f"\n[bold green] Searching for: [/bold green] {todo}")
            
            for result in all_search_results[todo]:
                console.print(f"   [blue]Title:[/blue] {result["title"]}")
                console.print(f"   [dim]URL:[/dim] {result["url"]}")
                console.print(f"   [blue]Summarizing...:[/blue] ")
                
                #start timer
                start = time.time()
                console.print(f"    [dim]Time taken: {start:.2f} seconds[/dim]")
                
                search_input = f"Title: {result["title"]} \n URL: {result["url"]}"
                agent_result = await Runner.run(searchExecutionAgent, input=search_input)
                
                search_response = SearchExecutionResponse(
                    title= result["title"],
                    url= result["url"],
                    summary= agent_result.final_output
                )

                self.search_responses.append(search_response)
                
                console.print(f"    [bold cyan]Summary: [/bold cyan] {agent_result.final_output + "..." if agent_result.final_output else "No summary available."}")
                #end timer
                end = time.time()
                console.print(f"    [dim]Time taken: {end - start:.2f} seconds[/dim]")
            
        console.print(f"Research Completed... {len(all_search_results)} sources found for {len(todos)} todos.")         
        
    async def deepresearch_final_report(self) -> str:
        input_string = f"Query: {self.query}\n Summary and Metadata: "
        for i, response in enumerate(self.search_responses, 1):
            input_string += f"{i}. Title: {response.title} \n URL: {response.url} \n Summary: {response.summary} \n"
            
        agent_result = await Runner.run(searchExecutionAgent, input=input_string)
        
        return agent_result.final_output
              
