from llm import create_gemini_client
from my_prompts.sarcasm_prompts import exp_prompt

async def ask_handler(ctx, msg):

    final_prompt = f"""
    {exp_prompt}\n
    Discord member prompt: {msg}
    Discord member id: {ctx.author.id}
    """

    try:
        response = create_gemini_client(prompt=final_prompt,request=msg,file_path="sarcasm.log")
    except Exception as e:
        response = "An error occurred while processing your request. Please try again later."
        print(e)

    await ctx.reply(response)