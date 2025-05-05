import os

import google.generativeai as genai
from dotenv import load_dotenv

from llms.llm_logging import log_entry


def create_gemini_client(
    sys_prompt: str,
    user_prompt: str,
    chat_history: list,
    file_path: str = "uninitialized.log",
    handler_name: str = "default handler",
) -> str:
    """
    Creates a chat completion request using Google's native Gemini API.

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
        print("\n-------------------------------------------\n")
        print("running", handler_name)
        # Configure the API key
        genai.configure(api_key=api_key)
        # Stronger system prompt to guide the model
        enhanced_sys_prompt = (
            sys_prompt
            + "\n\nIMPORTANT: Provide accurate and conversational responses based on the chat history."
        )
        gemini_pro25 = "gemini-2.5-pro-exp-03-25"
        gemini_pro20 = "gemini-2.0-pro-exp-02-05"
        gemini_flash = "gemini-2.0-flash"
        model = genai.GenerativeModel(
            model_name=gemini_flash, system_instruction=enhanced_sys_prompt
        )

        # Append the latest user prompt to the history
        chat_history.append({"role": "user", "parts": [user_prompt]})
        response = model.generate_content(
            chat_history, generation_config={"temperature": 0.2}
        )

        # Extract final text response
        final_response_part = response.candidates[0].content.parts[0]
        final_response = final_response_part.text

        # Append the final model response to the history
        chat_history.append({"role": "model", "parts": [final_response_part]})

        # Log the entry
        # Use a copy for logging to avoid excessive log size if history grows large
        log_history = chat_history[
            :-1
        ]  # Exclude the last model response for brevity in log
        log = f"SYSTEM_PROMPT: {enhanced_sys_prompt} HISTORY: {log_history} USER_PROMPT: {user_prompt} RESPONSE: {final_response}"
        log_entry(log, "info", file_path=file_path)

        return final_response

    except Exception as e:
        err_msg = f"Error calling Gemini API: {str(e)}"
        log_entry(err_msg, "error", file_path=file_path)
        raise Exception(err_msg)
