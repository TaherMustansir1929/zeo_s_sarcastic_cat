import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

from llm_logging import log_entry

def create_gemini_client(prompt: str, request: str = "", file_path: str = "sarcasm.log") -> str:
    """
    Creates a chat completion request using Google's native Gemini API.
    
    Args:
        prompt (str): The prompt to send to the model.
        file_path (str): The path to the file to open.
        request (str): The request made by th user.
        
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
        err_msg = "Google API key not found in.env file. Please add GEMINI_API_KEY to your.env file."
        log_entry(err_msg, "error")
        raise Exception(err_msg)

    try:
        client = genai.Client(api_key=api_key)
        config = types.GenerateContentConfig(
            tools=[]
        )

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config=config,
        )

        # Log the entry
        log = f"PROMPT: {request} RESPONSE: {response.text}"
        log_entry(log, "info", file_path=file_path)
        
        # Return the generated text
        return response.text
        
    except Exception as e:
        err_msg = f"Error calling Gemini API: {str(e)}"
        log_entry(err_msg, "error")
        raise Exception(err_msg)