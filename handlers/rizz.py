from my_prompts.rizz_prompts import rizz_prompt
from llm import create_gemini_client

async def rizz_handler(ctx):

    final_prompt = f"""
    {rizz_prompt}\n
    Discord member id: {ctx.author.id}
    """

    try:
        response = create_gemini_client(prompt=final_prompt,file_path="rizz.log")
    except Exception as e:
        response = "An error occurred while processing your request. Please try again later."
        print(e)

    await ctx.reply(response)