from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from langchain.tools import Tool
from llm_logging import log_entry
import functools

def log_tool_usage(func, tool_name):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        log_message = f"Tool used: {tool_name} with query: {args[0] if args else kwargs.get('query', 'No query')}"
        print(log_message)  # Log to terminal
        log_entry(log_message, 'info', file_path="langchain_agent.log")  # Log to file
        return func(*args, **kwargs)
    return wrapper

search = DuckDuckGoSearchRun()
search_tool = Tool(
    name="search_web",  # Changed from "Search Tool"
    func=log_tool_usage(search.run, "search_web"),
    description="Search the web for information"
)

api_wrapper = WikipediaAPIWrapper(top_k_results=3, doc_content_chars_max=2000)
wiki_tool = Tool(
    name="wikipedia",  # Changed from "Wikipedia Tool"
    func=log_tool_usage(WikipediaQueryRun(api_wrapper=api_wrapper).run, "wikipedia"),
    description="Search Wikipedia for information about a topic"
)
