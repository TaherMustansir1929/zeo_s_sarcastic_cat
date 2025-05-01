import os
from dotenv import load_dotenv
import google.generativeai as genai
from google.genai import types
from google.generativeai.types import FunctionDeclaration, Tool

from llms.llm_logging import log_entry
from llms.google_tools import web_search, wikipedia_search, web_search_func, wikipedia_search_func

# Tool configuration
gemini_tools = Tool(function_declarations=[web_search_func, wikipedia_search_func])

# Map function names to actual functions
tool_functions = {
    "web_search": web_search,
    "wikipedia_search": wikipedia_search,
}

def create_gemini_client(sys_prompt: str, user_prompt: str, chat_history: list, file_path: str = "uninitialized.log") -> str:
    """
    Creates a chat completion request using Google's native Gemini API with tool calling.

    Args:
        sys_prompt (str): The system prompt to guide the model.
        user_prompt (str): The latest user prompt.
        chat_history (list): A list of previous chat messages (alternating user/model roles).
                             Example: [{'role': 'user', 'parts': ['Hello']}, {'role': 'model', 'parts': ['Hi there!']}]
        file_path (str): The path to the log file.

    Returns:
        str: The generated response from the model.

    Raises:
        Exception: If API key is missing or API request fails.
    """
    # Load environment variables
    load_dotenv()

    # Get API key from .env file
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        err_msg = "Google API key not found in .env file. Please add GOOGLE_API_KEY to your .env file."
        log_entry(err_msg, "error", file_path=file_path)
        raise Exception(err_msg)

    try:
        genai.configure(api_key=api_key)
        # Stronger system prompt to encourage tool use for factual queries
        enhanced_sys_prompt = (
            sys_prompt +
            "\n\nIMPORTANT: For any factual, up-to-date, or knowledge-based queries (such as summarizing Wikipedia articles, current events, or when asked for facts), ALWAYS use the appropriate external tool (like 'wikipedia_search' or 'web_search') instead of relying on your own knowledge. Only answer directly if the information is purely conversational or creative."
        )
        model = genai.GenerativeModel(
            model_name='gemini-2.5-pro-exp-03-25',
            tools=[gemini_tools],
            system_instruction=enhanced_sys_prompt
        )

        # Append the latest user prompt to the history
        chat_history.append({'role': 'user', 'parts': [user_prompt]})

        response = model.generate_content(chat_history, generation_config={"temperature": 0.2})

        # Unified function call handling loop
        while hasattr(response.candidates[0].content.parts[0], 'function_call') and response.candidates[0].content.parts[0].function_call:
            function_call = response.candidates[0].content.parts[0].function_call
            function_name = function_call.name
            function_args = function_call.args

            if function_name in tool_functions:
                function_to_call = tool_functions[function_name]
                args_dict = {key: value for key, value in function_args.items()}
                try:
                    function_response = function_to_call(**args_dict)
                    chat_history.append({'role': 'model', 'parts': [response.candidates[0].content.parts[0]]})
                    chat_history.append({'role': 'function', 'parts': [
                        types.FunctionResponse(name=function_name, response={"content": function_response})
                    ]})
                    response = model.generate_content(chat_history)
                except Exception as e:
                    err_msg = f"Error executing tool {function_name}: {str(e)}"
                    log_entry(err_msg, "error", file_path=file_path)
                    return f"Error occurred while using tool '{function_name}': {str(e)}"
            else:
                err_msg = f"Unknown tool function called: {function_name}"
                log_entry(err_msg, "error", file_path=file_path)
                return "An internal error occurred: Unknown tool requested."

        # Extract final text response
        final_response_part = response.candidates[0].content.parts[0]
        final_response = final_response_part.text

        # Append the final model response to the history
        chat_history.append({'role': 'model', 'parts': [final_response_part]})

        # Log the entry
        # Use a copy for logging to avoid excessive log size if history grows large
        log_history = chat_history[:-1] # Exclude the last model response for brevity in log
        log = f"SYSTEM_PROMPT: {enhanced_sys_prompt} HISTORY: {log_history} USER_PROMPT: {user_prompt} RESPONSE: {final_response}"
        log_entry(log, "info", file_path=file_path)

        return final_response

    except Exception as e:
        err_msg = f"Error calling Gemini API: {str(e)}"
        log_entry(err_msg, "error", file_path=file_path)
        # Consider more specific error handling if needed
        raise Exception(err_msg)

# def create_gemini_client(prompt: str, request: str = "", file_path: str = "sarcasm.log") -> str:
#     """
#     Creates a chat completion request using Google's native Gemini API.
    
#     Args:
#         prompt (str): The prompt to send to the model.
#         file_path (str): The path to the file to open.
#         request (str): The request made by th user.
        
#     Returns:
#         str: The generated response from the model.
        
#     Raises:
#         Exception: If API key is missing or API request fails.
#     """
#     # Load environment variables
#     load_dotenv()
    
#     # Get API key from .env file
#     api_key = os.getenv("GOOGLE_API_KEY")
#     if not api_key:
#         err_msg = "Google API key not found in.env file. Please add GEMINI_API_KEY to your.env file."
#         log_entry(err_msg, "error")
#         raise Exception(err_msg)

#     try:
#         client = genai.Client(api_key=api_key)
#         config = types.GenerateContentConfig(
#             tools=[]
#         )

#         response = client.models.generate_content(
#             model="gemini-2.0-flash",
#             contents=prompt,
#             config=config,
#         )

#         # Log the entry
#         log = f"PROMPT: {request} RESPONSE: {response.text}"
#         log_entry(log, "info", file_path=file_path)
        
#         # Return the generated text
#         return response.text
        
#     except Exception as e:
#         err_msg = f"Error calling Gemini API: {str(e)}"
#         log_entry(err_msg, "error")
#         raise Exception(err_msg)