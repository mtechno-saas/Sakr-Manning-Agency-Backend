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
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from .tools import tools
import os

# Use Google Gemini
model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=os.environ.get("GOOGLE_API_KEY", "missing_key_please_add_to_env"))

# System prompt for the chat agent
SYSTEM_PROMPT = """You are a conversational AI Search Agent designed to help users find information through natural dialogue.

Your personality and approach:
- Friendly, helpful, and conversational
- Remember context from previous messages in the conversation
- Ask clarifying questions when needed
- Provide comprehensive but digestible answers
- Suggest follow-up topics or related questions
- Acknowledge when you don't know something and search for it

Your search capabilities:
- WebSearch: Real-time web search for current information
- WikipediaSearch: Encyclopedia knowledge for background information  
- ConversationalSearch: Context-aware search for follow-up questions
- NewsSearch: Recent news and current events
- ResearchSearch: Academic and detailed information
- FactCheck: Verify claims and statements
- FollowUpQuestions: Generate relevant conversation continuations

Chat guidelines:
1. Always maintain conversation context and refer back to previous messages when relevant
2. Use the most appropriate search tool based on the user's question and conversation history
3. For follow-up questions, use ConversationalSearch to maintain topic continuity
4. Provide sources and citations when possible
5. If information seems outdated or uncertain, mention this and search for updates
6. End responses with relevant follow-up questions or suggestions when appropriate
7. Be concise but thorough - aim for helpful, not overwhelming responses
8. Remember user preferences and interests shown throughout the conversation

Always be helpful, accurate, and engaging in your responses!"""

# Create the agent (without state_modifier which is not supported)
agent = create_react_agent(model, tools)

def format_conversation_history(messages):
    """Format conversation history for the agent"""
    formatted_messages = []
    
    # Add system message first
    formatted_messages.append(SystemMessage(content=SYSTEM_PROMPT))
    
    for message in messages:
        if hasattr(message, 'role') and hasattr(message, 'content'):
            if message.role == 'user':
                formatted_messages.append(HumanMessage(content=message.content))
            elif message.role == 'assistant':
                formatted_messages.append(AIMessage(content=message.content))
        elif hasattr(message, 'message_type') and hasattr(message, 'content'):
            if message.message_type == 'user':
                formatted_messages.append(HumanMessage(content=message.content))
            elif message.message_type == 'assistant':
                formatted_messages.append(AIMessage(content=message.content))
    
    return formatted_messages

def extract_conversation_context(messages, limit=5):
    """Extract recent conversation context"""
    if not messages:
        return ""
    
    recent_messages = list(messages.order_by('-timestamp')[:limit])
    context_parts = []
    
    for message in reversed(recent_messages):
        role = "User" if message.role == 'user' else "Assistant"
        content = message.content[:100] + "..." if len(message.content) > 100 else message.content
        context_parts.append(f"{role}: {content}")
    
    return "\n".join(context_parts)

def get_agent_response(query, conversation_history=None, session_id=None):
    """Get response from the agent with conversation context"""
    try:
        # Prepare messages
        messages = []
        
        # Add system message
        messages.append(SystemMessage(content=SYSTEM_PROMPT))
        
        # Add conversation history if available
        if conversation_history:
            for msg in conversation_history:
                if msg.role == 'user':
                    messages.append(HumanMessage(content=msg.content))
                elif msg.role == 'assistant':
                    messages.append(AIMessage(content=msg.content))
        
        # Add current query
        messages.append(HumanMessage(content=query))
        
        # Get response from agent
        response = agent.invoke({"messages": messages})
        
        # Extract the final message content
        if response and "messages" in response:
            final_message = response["messages"][-1]
            if hasattr(final_message, 'content'):
                return final_message.content
            else:
                return str(final_message)
        
        return "I apologize, but I couldn't generate a proper response. Please try again."
        
    except Exception as e:
        return f"I encountered an error while processing your request: {str(e)}"