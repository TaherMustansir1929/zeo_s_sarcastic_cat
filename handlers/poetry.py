from llms.genai import new_gemini_client
from my_prompts.poetry_prompts import poetry_prompt


async def poetry_handler(ctx, msg, chat_histories_poetry):
    user_id = ctx.author.id
    if user_id not in chat_histories_poetry:
        chat_histories_poetry[user_id] = []

    final_prompt = f"""
        {poetry_prompt}
        Discord User ID = {ctx.author.id}
        User Prompt for poetry(shayri) topic = {msg}
    """

    try:
        response, updated_chat_history = new_gemini_client(
            sys_prompt=final_prompt,
            user_prompt=msg,
            file_path="poetry.log",
            chat_history=chat_histories_poetry[user_id],
            handler_name="poetry_handler",
        )

        # Update the chat history with the new user message and response
        chat_histories_poetry[user_id] = updated_chat_history

        # Keep only the last 10 interactions to prevent the history from getting too large
        if len(chat_histories_poetry[user_id]) > 10:
            chat_histories_poetry[user_id] = chat_histories_poetry[user_id][-10:]

    except Exception as e:
        response = (
            "An error occurred while processing your request. Please try again later."
        )
        print(e)

    await ctx.reply(response)
