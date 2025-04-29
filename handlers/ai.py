from llm import create_gemini_client
from my_prompts.ai_prompts import ai_prompt


async def ai_handler(ctx, msg):

    final_prompt = f"""
    {ai_prompt}\n
    Discord User id: {ctx.author.id}
    Discord User's chat: {msg}
    """

    try:
        response = create_gemini_client(prompt=final_prompt,request=msg,file_path="ai.log")
    except Exception as e:
        response = "An error occurred while processing your request. Please try again later."
        print(e)

    await ctx.reply(response)