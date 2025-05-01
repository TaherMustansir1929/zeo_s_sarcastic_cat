from dotenv import load_dotenv
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.messages import BaseMessage

from llms.llm_logging import log_entry
from llms.tools import search_tool, wiki_tool

load_dotenv()

class AskCommandResponse(BaseModel):
    response: str
    tools_used: list[str]

def langchain_api(prompt: str, request: str = "", file_path: str = "sarcasm.log", chat_history: list[BaseMessage] = None) -> str:
    """
        Creates a chat completion request using Google's native Gemini API.

        Args:
            prompt (str): The prompt to send to the model.
            file_path (str): The path to the file to open.
            request (str): The request made by th user.
            chat_history (list[BaseMessage]): The chat history for the conversation as a list of BaseMessage objects.

        Returns:
            str: The generated response from the model.

        Raises:
            Exception: If API key is missing or API request fails.
        """
    if chat_history is None:
        chat_history = []

    gemini_pro_1 = "gemini-2.0-pro-exp-02-05"
    gemini_pro_2 = "gemini-2.5-pro-exp-03-25"
    gemini_flash = "gemini-2.0-flash"

    llm = ChatGoogleGenerativeAI(model=gemini_pro_2, temperature=0.5, max_tokens=None, timeout=None, max_retries=2)

    sys_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", prompt
                # "You are a helpful AI assistant. When you don't know something or need to find information, use the search_web or wikipedia tools available to you. Always use these tools when asked about current events, facts, or information you're unsure about.",
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{query}"),
            ("placeholder", "{agent_scratchpad}"),
        ]
    )

    tools_list = [search_tool, wiki_tool]
    agent = create_tool_calling_agent(
        llm=llm,
        prompt=sys_prompt,
        tools=tools_list
    )

    agent_executor = AgentExecutor(agent=agent, tools=tools_list, verbose=True)
    try:
        raw_response = agent_executor.invoke(
            {
                "query": request,
                "chat_history": chat_history
            },
            return_intermediate_steps=True
        )

        # Extract tool usage information from intermediate steps
        tools_used = []
        if "intermediate_steps" in raw_response:
            for step in raw_response["intermediate_steps"]:
                if step[0].tool != "_Exception":
                    tools_used.append(f"{step[0].tool}: {step[0].tool_input}")

        # Log the prompt, response, and tool usage
        log = f"PROMPT: {request} RESPONSE: {raw_response.get('output')} TOOLS_USED: {', '.join(tools_used) if tools_used else 'None'}"
        # Log to the specified file (for backward compatibility)
        log_entry(log, "info", file_path=file_path)
        # Also log to langchain_agent.log
        log_entry(log, "info", file_path="langchain_agent.log")

        return str(raw_response.get("output"))

    except Exception as e:
        return f"An error occurred: {e}"
