from llms.genai import new_gemini_client
from my_prompts.rizz_prompts import rizz_prompt


async def rizz_handler(ctx):
    final_prompt = f"""
    {rizz_prompt}\n
    Discord member id: {ctx.author.id}
    """

    try:
        response, _ = new_gemini_client(
            sys_prompt=final_prompt,
            user_prompt="rizz me up freaky",
            file_path="rizz.log",
            chat_history=[],
            handler_name="rizz_handler",
        )
    except Exception as e:
        response = (
            "An error occurred while processing your request. Please try again later."
        )
        print(e)

    await ctx.reply(response)

