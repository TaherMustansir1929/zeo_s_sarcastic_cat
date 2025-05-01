from llms.langchain_api import langchain_api
from langchain_core.messages import HumanMessage, AIMessage

from my_prompts.ai_prompts import ai_prompt

async def smart_ai_handler(ctx, msg, chat_histories_ai):
    user_id = str(ctx.author.id)

    # Initialize chat history for this user if it doesn't exist
    if user_id not in chat_histories_ai:
        chat_histories_ai[user_id] = []

    final_prompt = f"""
        {ai_prompt}\n
        Discord User's chat: {msg}
        """
    # Discord User id: {ctx.author.id}

    # Format chat history for the LLM as a list of message objects
    formatted_history = []
    if chat_histories_ai[user_id]:
        for entry in chat_histories_ai[user_id]:
            formatted_history.append(HumanMessage(content=entry['user']))
            formatted_history.append(AIMessage(content=entry['ai']))

    try:
        response = langchain_api(prompt=final_prompt, request=msg, file_path="ai.log", chat_history=formatted_history)

        # Update chat history with this interaction
        chat_histories_ai[user_id].append({
            "user": msg,
            "ai": response
        })

        # Keep only the last 10 interactions to prevent the history from getting too large
        if len(chat_histories_ai[user_id]) > 10:
            chat_histories_ai[user_id] = chat_histories_ai[user_id][-10:]

    except Exception as e:
        response = "An error occurred while processing your request. Please try again later."
        print(e)

    await ctx.reply(response)