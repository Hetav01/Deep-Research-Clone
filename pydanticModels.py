from pydantic import BaseModel
from typing import List

class SearchExecutionResponse(BaseModel):
    title: str
    url: str
    summary: str
    
class TodoResponse(BaseModel):
    queries: List[str]
    thoughts: str