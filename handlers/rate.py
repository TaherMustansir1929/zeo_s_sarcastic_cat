from llms.genai import new_gemini_client
from my_prompts.rate_rizz_prompts import rate_prompt


async def rate_handler(ctx, msg):
    final_prompt = f"""
    {rate_prompt}\n
    Discord user pickup line: {msg}
    Discord user id: {ctx.author.id}
    """

    try:
        response, _ = new_gemini_client(
            sys_prompt=final_prompt,
            user_prompt=msg,
            file_path="rate.log",
            chat_history=[],
            handler_name="rate_handler",
        )
    except Exception as e:
        response = (
            "An error occurred while processing your request. Please try again later."
        )
        print(e)

    await ctx.reply(response)
