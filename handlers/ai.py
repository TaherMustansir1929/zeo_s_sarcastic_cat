from llms.genai import new_gemini_client
from my_prompts.ai_prompts import ai_prompt


async def ai_handler(ctx, msg, chat_histories_ai_google_sdk):
    user_id = str(ctx.author.id)

    # Initialize chat history for this user if it doesn't exist
    if user_id not in chat_histories_ai_google_sdk:
        chat_histories_ai_google_sdk[user_id] = []

    final_prompt = f"""
    {ai_prompt}\n
    Discord User id: {ctx.author.id}
    Discord User's chat: {msg}
    """

    try:
        response, updated_chat_history = new_gemini_client(
            sys_prompt=final_prompt,
            user_prompt=msg,
            file_path="ai.log",
            chat_history=chat_histories_ai_google_sdk[user_id],
            handler_name="ai_handler",
        )

        # Update the chat history with the new user message and response
        chat_histories_ai_google_sdk[user_id] = updated_chat_history

        # Keep only the last 10 interactions to prevent the history from getting too large
        if len(chat_histories_ai_google_sdk[user_id]) > 10:
            chat_histories_ai_google_sdk[user_id] = chat_histories_ai_google_sdk[
                user_id
            ][-10:]

    except Exception as e:
        response = (
            "An error occurred while processing your request. Please try again later."
        )
        print(e)

    await ctx.send(response)

