# ai_agents/tools.py
from langchain_core.tools import Tool
from langchain_core.tools import StructuredTool
from langchain_community.tools import DuckDuckGoSearchRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from pydantic import BaseModel, Field
import requests
import json
from datetime import datetime
import re
import uuid

# --- Free Search Tools (No API Keys Required) ---

# DuckDuckGo Search
duckduckgo = DuckDuckGoSearchRun()

def run_duckduckgo(query: str) -> str:
    return duckduckgo.run(query)

websearch_tool = Tool(
    name="WebSearch",
    func=run_duckduckgo,
    description="Search the web for current information, news, facts, and general queries. Use this for real-time information and recent events."
)

# Wikipedia Search
wikipedia = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

def run_wikipedia(query: str) -> str:
    return wikipedia.run(query)

wikipedia_tool = Tool(
    name="WikipediaSearch",
    func=run_wikipedia,
    description="Search Wikipedia for detailed information about topics, people, places, concepts, and historical facts. Great for comprehensive background information."
)

# --- Structured Search Tools ---

class DetailedSearchInput(BaseModel):
    query: str = Field(..., description="The search query")
    context: str = Field(default="", description="Additional context from the conversation")

def detailed_websearch(query: str, context: str = ""):
    """Perform a detailed web search with conversation context."""
    try:
        # Enhance query with context if provided
        enhanced_query = f"{query} {context}".strip() if context else query
        results = duckduckgo.run(enhanced_query)

        return {
            "query": query,
            "enhanced_query": enhanced_query,
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "source": "DuckDuckGo",
            "search_type": "detailed_web"
        }
    except Exception as e:
        return {"error": f"Search failed: {str(e)}", "query": query}

detailed_search_tool = StructuredTool.from_function(
    func=detailed_websearch,
    args_schema=DetailedSearchInput,
    description="Perform a detailed web search with conversation context for more relevant results."
)

# --- Conversational Search Tool ---
class ConversationalSearchInput(BaseModel):
    query: str = Field(..., description="Current user query")
    conversation_history: str = Field(default="", description="Previous conversation context")

def conversational_search(query: str, conversation_history: str = ""):
    """Search with full conversation context for follow-up questions."""
    try:
        # Analyze if this is a follow-up question
        follow_up_indicators = ["what about", "how about", "tell me more", "explain", "elaborate", "also", "and"]
        is_follow_up = any(indicator in query.lower() for indicator in follow_up_indicators)

        if is_follow_up and conversation_history:
            # Extract key topics from conversation history
            search_query = f"{conversation_history[-200:]} {query}"  # Last 200 chars of context
        else:
            search_query = query

        results = duckduckgo.run(search_query)

        return {
            "query": query,
            "search_query": search_query,
            "is_follow_up": is_follow_up,
            "results": results,
            "timestamp": datetime.now().isoformat(),
            "search_type": "conversational"
        }
    except Exception as e:
        return {"error": f"Conversational search failed: {str(e)}", "query": query}

conversational_search_tool = StructuredTool.from_function(
    func=conversational_search,
    args_schema=ConversationalSearchInput,
    description="Search with conversation context to handle follow-up questions and maintain topic continuity."
)

# --- News Search Tool ---
class NewsSearchInput(BaseModel):
    topic: str = Field(..., description="News topic to search for")
    timeframe: str = Field(default="recent", description="Time frame: recent, today, week, month")

def search_news(topic: str, timeframe: str = "recent"):
    """Search for news with specified timeframe."""
    try:
        time_modifiers = {
            "today": "today",
            "recent": "recent",
            "week": "past week",
            "month": "past month"
        }

        time_mod = time_modifiers.get(timeframe, "recent")
        query = f"{topic} news {time_mod}"
        results = duckduckgo.run(query)

        return {
            "topic": topic,
            "timeframe": timeframe,
            "news_results": results,
            "search_type": "news",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"News search failed: {str(e)}", "topic": topic}

news_search_tool = StructuredTool.from_function(
    func=search_news,
    args_schema=NewsSearchInput,
    description="Search for recent news and current events with specified timeframe."
)

# --- Research Search Tool ---
class ResearchSearchInput(BaseModel):
    topic: str = Field(..., description="Research topic or academic subject")
    depth: str = Field(default="medium", description="Depth level: basic, medium, comprehensive")

def research_search(topic: str, depth: str = "medium"):
    """Search for academic and research information with specified depth."""
    try:
        # Get Wikipedia info for foundational knowledge
        wiki_results = wikipedia.run(topic)

        # Enhance web search based on depth
        depth_modifiers = {
            "basic": f"{topic} overview introduction",
            "medium": f"{topic} research academic study",
            "comprehensive": f"{topic} comprehensive analysis research papers academic studies"
        }

        web_query = depth_modifiers.get(depth, depth_modifiers["medium"])
        web_results = duckduckgo.run(web_query)

        return {
            "topic": topic,
            "depth": depth,
            "wikipedia_info": wiki_results,
            "research_results": web_results,
            "search_type": "research",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Research search failed: {str(e)}", "topic": topic}

research_search_tool = StructuredTool.from_function(
    func=research_search,
    args_schema=ResearchSearchInput,
    description="Search for academic and research information with adjustable depth level."
)

# --- Fact Checking Tool ---
class FactCheckInput(BaseModel):
    statement: str = Field(..., description="Statement or claim to fact-check")
    context: str = Field(default="", description="Additional context for fact-checking")

def fact_check(statement: str, context: str = ""):
    """Fact-check a statement using multiple sources."""
    try:
        # Search for fact-checking sources
        fact_query = f'"{statement}" fact check verify truth'
        if context:
            fact_query += f" {context}"

        web_results = duckduckgo.run(fact_query)

        # Also search Wikipedia for reference information
        wiki_keywords = statement.split()[:5]  # First 5 words for Wikipedia
        wiki_results = wikipedia.run(" ".join(wiki_keywords))

        return {
            "statement": statement,
            "context": context,
            "fact_check_results": web_results,
            "reference_info": wiki_results,
            "search_type": "fact_check",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Fact check failed: {str(e)}", "statement": statement}

fact_check_tool = StructuredTool.from_function(
    func=fact_check,
    args_schema=FactCheckInput,
    description="Fact-check statements and claims using multiple reliable sources with context."
)

# --- Follow-up Question Generator ---
class FollowUpInput(BaseModel):
    topic: str = Field(..., description="Current topic being discussed")
    user_interest: str = Field(default="", description="User's apparent interest or focus")

def generate_follow_up_questions(topic: str, user_interest: str = ""):
    """Generate relevant follow-up questions to continue the conversation."""
    try:
        # Search for related topics and common questions
        query = f"{topic} related questions common queries"
        if user_interest:
            query += f" {user_interest}"

        results = duckduckgo.run(query)

        # Generate some standard follow-up patterns
        follow_ups = [
            f"Would you like to know more about {topic}?",
            f"Are you interested in recent developments regarding {topic}?",
            f"Would you like me to search for specific aspects of {topic}?",
        ]

        return {
            "topic": topic,
            "suggested_questions": follow_ups,
            "related_info": results,
            "search_type": "follow_up",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {"error": f"Follow-up generation failed: {str(e)}", "topic": topic}

follow_up_tool = StructuredTool.from_function(
    func=generate_follow_up_questions,
    args_schema=FollowUpInput,
    description="Generate relevant follow-up questions to continue the conversation naturally."
)

# --- Tools list ---
tools = [
    websearch_tool,
    wikipedia_tool,
    detailed_search_tool,
    conversational_search_tool,
    news_search_tool,
    research_search_tool,
    fact_check_tool,
    follow_up_tool,
]