import os
import time

import google.generativeai as genai
from dotenv import load_dotenv

# Assuming llms.llm_logging exists and has the log_entry function
from llms.llm_logging import log_entry

# Import Content and Part types if you need more explicit control,
# but the SDK often handles dict conversion automatically.
# from google.ai import generativelanguage as glm

# Define a type hint for the history structure for clarity
ChatHistoryType = list[
    dict[str, str | list[str]]
]  # List of {'role': ..., 'parts': [...]}

def new_gemini_client(
    sys_prompt: str,
    user_prompt: str,
    chat_history: ChatHistoryType,
    file_path: str = "uninitialized.log",
    handler_name: str = "default handler",
) -> tuple[str, ChatHistoryType]:
    """
    Creates a chat completion request using Google's newer google-generativeai SDK.

    Uses the chat session (`start_chat`, `send_message`) pattern.

    Args:
        sys_prompt (str): The system prompt to guide the model.
        user_prompt (str): The latest user prompt.
        chat_history (ChatHistoryType): A list of previous chat messages (alternating user/model roles).
                                        Example: [{'role': 'user', 'parts': ['Hello']}, {'role': 'model', 'parts': ['Hi there!']}]
                                        Note: The SDK typically handles conversion from this dict format.
        file_path (str): The path to the log file.
        handler_name (str): Identifier for the handler calling this function.

    Returns:
        tuple[str, ChatHistoryType]: A tuple containing:
            - str: The generated response text from the model.
            - ChatHistoryType: The updated chat history including the latest user prompt and model response.

    Raises:
        ValueError: If API key is missing.
        google.api_core.exceptions.GoogleAPIError: If the API request fails for API-related reasons.
        Exception: For other potential errors during execution.
    """

    # Record Function start time
    start_time = time.time()

    # Load environment variables
    load_dotenv()

    # Get API key from .env file
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        err_msg = "Google API key not found in .env file. Please add GOOGLE_API_KEY to your .env file."
        # Use a dedicated logger if available, otherwise use the provided log_entry
        log_entry(err_msg, "error", file_path=file_path)
        # Consider raising a more specific error like ValueError
        raise ValueError(err_msg)

    try:
        print("\n-------------------------------------------\n")
        print("running", handler_name)

        # Configure the API key
        genai.configure(api_key=api_key)

        # Enhance system prompt (same as before)
        enhanced_sys_prompt = (
            sys_prompt
            + "\n\nIMPORTANT: Provide accurate and conversational responses based on the chat history."
        )

        # --- Model Selection ---
        # Experimental models (may change or require allowlisting)
        models = ["gemini-2.0-flash", "gemini-2.5-pro-exp-03-25", "gemini-2.0-pro-exp-02-05"]

        selected_model = models[0]  # Defaulting to flash

        model = genai.GenerativeModel(
            model_name=selected_model,
            system_instruction=enhanced_sys_prompt,
            # safety_settings=... # Optional: configure safety settings if needed
            # generation_config=... # Optional: default generation config can be set here
        )

        # --- Start Chat Session ---
        # The SDK's start_chat can usually handle the list of dictionaries format.
        # If issues arise, explicitly convert chat_history to list[glm.Content].
        chat_session = model.start_chat(history=chat_history)

        # --- Send User Message ---
        # Send the new user prompt to the ongoing chat session
        # Generation config can be passed here to override model defaults for this specific call
        response = chat_session.send_message(
            user_prompt, generation_config=genai.types.GenerationConfig(temperature=0.2)
        )

        # --- Extract Response ---
        # The response object from send_message directly contains the text
        final_response = response.text

        # --- History Management ---
        # The chat_session.history attribute now automatically contains the full history,
        # including the latest user prompt and the model's response.
        # We need to convert it back to the simple dict format if the caller expects that.
        updated_history_sdk_format = chat_session.history
        updated_history_dict_format: ChatHistoryType = [
            {"role": msg.role, "parts": [part.text for part in msg.parts]}
            for msg in updated_history_sdk_format
        ]

        # --- Logging ---
        # Log the context before the *latest* model response for brevity
        # The history used for the call includes the latest user prompt.

        log = (
            f"USER_PROMPT: {user_prompt} "
            f"RESPONSE: {final_response}"
        )
        log_entry(log, "info", file_path=file_path)

        # Log function execution time:
        performance_log = f"{handler_name} executed in {(time.time() - start_time):.4f} seconds"
        print(performance_log)

        # Return the response text and the fully updated history
        debug_response = f"{final_response} \n `{' '.join(performance_log.split()[1:])}`"
        return debug_response, updated_history_dict_format

    # Catch more specific API errors if possible, fallback to generic Exception
    except (genai.APIError, Exception) as e:
        # Log the specific error type if available
        error_type = type(e).__name__
        err_msg = f"Error calling Gemini API ({error_type}): {str(e)}"
        log_entry(err_msg, "error", file_path=file_path)
        # Re-raise the original exception or a custom one
        # Re-raising preserves the original stack trace which can be helpful
        raise Exception(err_msg) from e  # Chain the exception
