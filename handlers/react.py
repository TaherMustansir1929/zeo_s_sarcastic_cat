from langchain_core.messages import HumanMessage, AIMessage

from llms.langchain_api import langchain_api
from my_prompts.react_prompts import react_prompt

async def react_handler(ctx, msg, chat_histories_google_sdk):
    user_id = str(ctx.author.id)

    if user_id not in chat_histories_google_sdk:
        await ctx.reply("Hold up!🤨 What are you reacting to? Maybe you forgot to ask a question first dumbass🙄")
        return

    final_prompt = f"""
                {react_prompt}\n
                Discord member id: {ctx.author.id}
                """

    try:
        response = langchain_api(prompt=final_prompt, request=msg, file_path="react.log",
                                 chat_history=chat_histories_google_sdk)

    except Exception as e:
        response = "An error occurred while processing your request. Please try again later."
        print(e)

    await ctx.reply(response)