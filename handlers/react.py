from langchain_core.messages import HumanMessage, AIMessage

from langchain_api import langchain_api
from my_prompts.react_prompts import react_prompt

async def react_handler(ctx, msg, chat_histories_ask):
    user_id = str(ctx.author.id)

    if user_id not in chat_histories_ask:
        await ctx.reply("Hold up!🤨 What are you reacting to? Maybe you forgot to ask a question first dumbass🙄")
        return

    final_prompt = f"""
                {react_prompt}\n
                Discord member id: {ctx.author.id}
                """

    formatted_history = [HumanMessage(content=chat_histories_ask[user_id][-1]['user']),
                         AIMessage(content=chat_histories_ask[user_id][-1]['ai'])]

    try:
        response = langchain_api(prompt=final_prompt, request=msg, file_path="react.log",
                                 chat_history=formatted_history)

    except Exception as e:
        response = "An error occurred while processing your request. Please try again later."
        print(e)

    await ctx.reply(response)