# ai_agents/agent.py
# from langchain.agents import initialize_agent
# from langchain_ollama import OllamaLLM
# from .tools import tools

# llm = OllamaLLM(model="gemma3:1b")  # You can swap with another local Ollama model

# agent = initialize_agent(
#     tools=tools,
#     llm=llm,
#     agent="zero-shot-react-description",
#     verbose=True,
#     handle_parsing_errors=True,
# )

# ai_agents/agent.py
from langgraph.prebuilt import create_react_agent
from langchain_ollama import ChatOllama
from .tools import tools

# Use Gemma 3 1B model
model = ChatOllama(model="gemma3:1b")

agent = create_react_agent(
    model,
    tools
)

