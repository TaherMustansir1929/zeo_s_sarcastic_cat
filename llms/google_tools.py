import requests
import urllib.parse
import wikipedia # Add import
from bs4 import BeautifulSoup
from google.generativeai.types import FunctionDeclaration

# Placeholder functions for tools - replace with actual implementations
def web_search(query: str) -> str:
    """Performs a web search for the given query using DuckDuckGo and BeautifulSoup."""
    print(f"--- Executing Web Search: {query} ---")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    # Use html version of DDG for simpler parsing
    search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote_plus(query)}"
    results_text = f"Web search results for '{query}':\n\n"
    max_results = 5  # Limit the number of results

    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')

        # Find result containers (selector for DDG's HTML version)
        result_divs = soup.find_all('div', class_='result')

        count = 0
        for result in result_divs:
            if count >= max_results:
                break

            title_tag = result.find('a', class_='result__a')
            snippet_tag = result.find('a', class_='result__snippet') # Snippet is often within the same link
            link_tag = title_tag # Link is usually the href of the title tag

            if title_tag and snippet_tag and link_tag and 'href' in link_tag.attrs:
                title = title_tag.get_text(strip=True)
                link = link_tag['href']
                snippet = snippet_tag.get_text(strip=True)

                # Clean up DDG redirect links (extract the 'uddg' parameter)
                parsed_link = urllib.parse.urlparse(link)
                qs = urllib.parse.parse_qs(parsed_link.query)
                if 'uddg' in qs:
                    link = qs['uddg'][0]

                results_text += f"Title: {title}\n"
                results_text += f"Snippet: {snippet}\n"
                results_text += f"Link: {link}\n\n"
                count += 1

        if count == 0:
             results_text += "No results found or could not parse results."

    except requests.exceptions.Timeout:
        print(f"Error during web search request for '{query}': Timeout")
        return f"Error performing web search for '{query}': Request timed out."
    except requests.exceptions.RequestException as e:
        print(f"Error during web search request for '{query}': {e}")
        return f"Error performing web search for '{query}': Network issue ({e})."
    except Exception as e:
        # Catch potential BeautifulSoup errors or other unexpected issues
        print(f"Error parsing web search results for '{query}': {e}")
        return f"Error performing web search for '{query}': Parsing issue ({e})."

    return results_text.strip()

def wikipedia_search(query: str) -> str:
    """Searches Wikipedia for the given query and returns a summary."""
    print(f"--- Executing Wikipedia Search: {query} ---")
    try:
        # Limit summary to 3 sentences for brevity
        summary = wikipedia.summary(query, sentences=3)
        page = wikipedia.page(query, auto_suggest=False) # Get page to provide URL
        results_text = f"Wikipedia summary for '{query}':\n\n{summary}\n\nSource: {page.url}"
        return results_text
    except wikipedia.exceptions.PageError:
        print(f"Wikipedia page not found for '{query}'")
        return f"Could not find a Wikipedia page for '{query}'. Please try a different search term."
    except wikipedia.exceptions.DisambiguationError as e:
        print(f"Wikipedia search for '{query}' resulted in disambiguation: {e.options[:5]}")
        # Return the first few options to the user
        options_text = ", ".join(e.options[:5])
        return f"Your search '{query}' could refer to multiple topics: {options_text}. Please be more specific."
    except Exception as e:
        print(f"Error during Wikipedia search for '{query}': {e}")
        return f"An unexpected error occurred during the Wikipedia search for '{query}': {e}"

# Define tool schemas for the Gemini model
web_search_func = FunctionDeclaration(
    name="web_search",
    description="Search the web for information.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query."}
        },
        "required": ["query"]
    }
)

wikipedia_search_func = FunctionDeclaration(
    name="wikipedia_search",
    description="Search Wikipedia for information.",
    parameters={
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "The search query."}
        },
        "required": ["query"]
    }
)