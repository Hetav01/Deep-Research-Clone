from agents import Agent, function_tool
from bs4 import BeautifulSoup
import requests
from pydantic import BaseModel
from pydanticModels import SearchExecutionResponse

# this tool is a basic scraper and is not very advanced at scraping text from diverse sources. For such usage, you might need to use Tavily end-to-end.
# that might help develop a more advanced scraper that can handle different types of content and formats. It is an expensive tool, so use it wisely.

@function_tool
def scraper(url: str) -> str:
    """Scarper tool for llms to extract text from a webpage."""
    
    try: 
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        
        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for script in soup(["script", "style"]):
                script.extract()
            
            text = soup.get_text(separator=" ", strip=True)
            
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:6000] if len(text) > 6000 else text
        except ImportError:
            return response.text[:6000]
    except Exception as e:
        return f"Failed to scrape {url}: {str(e)}"
    

SEARCH_AGENT_PROMPT = """
    You are a search execution agent, an elite information-scouting assistant. Given a URL and its title, your job is to analyze the content of the URL and provide a summary of the key points.
    The summary must be 2-4 paragraphs.
    Write the summary in a clean and clear manner, ensuring that it captures the essence of the content. You're not required to have proper grammar or sentence structure. This will be consumed by someone synthesizing a report, so it's vital to capture the main points from the URL.
    Ignore any fluff that is not related to the main topic. and do not include additional commentary other than the summary.
    Be sure to use the tool provided to scrape the URL and extract the text content.
    
    YOUR TASK
    Turn the extracted text into a high-signal summary that a human synthesiser can slot directly into a larger report.

    OUTPUT – USE THIS EXACT TEMPLATE
    ### Summary
    <2–4 paragraphs (≈200-400 words each). Paraphrase core arguments, data, claims, conclusions, and named entities.  
    You may blend in **≤100 words** of clearly-marked background knowledge that you might have on the topic to give context. 

    ### Meta
    - **Source Type**: <peer-reviewed | gov report | news article | company blog | opinion | unknown>  
    - **Article Date**: <YYYY-MM-DD | unknown>  

    RULES
    1. **Think first**: identify the article’s primary purpose, key facts, and unique insights.  
    2. Strip out navigation text, ads, unrelated anecdotes, and duplicated sentences.  
    3. Paraphrase; do **not** quote more than three consecutive words verbatim.  
    4. Neutral, third-person voice only—no personal commentary or opinion.  
    5. If content is empty, paywalled, or non-English, output exactly  
"""

# class SearchExecutionResponse(BaseModel):
#     search_results: str
#     thoughts: str

# instead of this we'll make another file to directly store the results so that we can use that in the final reporting agent too.

# output_type= SearchExecutionResponse,
searchExecutionAgent = Agent(
    name= "Search Execution Agent",
    instructions=SEARCH_AGENT_PROMPT,
    tools= [scraper],
    model= "gpt-4o",
)