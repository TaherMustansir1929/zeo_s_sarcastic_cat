from llms.genai import new_gemini_client
from my_prompts.react_prompts import react_prompt


async def react_handler(ctx, msg, chat_histories_google_sdk):
    user_id = str(ctx.author.id)

    if user_id not in chat_histories_google_sdk:
        await ctx.reply(
            "Hold up!🤨 What are you reacting to? Maybe you forgot to ask a question first dumbass🙄"
        )
        return

    final_prompt = f"{react_prompt}\nDiscord member id: {ctx.author.id}"

    try:
        response, _ = new_gemini_client(
            sys_prompt=final_prompt,
            user_prompt=msg,
            file_path="react.log",
            chat_history=chat_histories_google_sdk[user_id],
            handler_name="react_handler",
        )

    except Exception as e:
        response = (
            "An error occurred while processing your request. Please try again later."
        )
        print(e)

    await ctx.reply(response)
