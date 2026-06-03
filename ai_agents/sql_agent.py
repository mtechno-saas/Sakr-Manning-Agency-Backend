import json
import logging
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from .db_utils import get_abbreviated_schema, execute_read_only_query
from .models import QueryCache, FailedQueryLog
import os

logger = logging.getLogger(__name__)

# Use the same model as in agent.py
model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=os.environ.get("GOOGLE_API_KEY", "missing_key_please_add_to_env"))

SQL_GENERATION_PROMPT = """You are a highly skilled SQL data analyst for a maritime manning agency.
Your task is to generate a valid SQLite SQL query based on the provided user question and database schema.
Return ONLY the raw SQL query. Do not include any explanations, markdown formatting (like ```sql), or comments.
Ensure the query is a SELECT statement and uses the provided table and column names exactly.

IMPORTANT DOMAIN KNOWLEDGE:
- Seafarers/users are stored in the "api_users" table.
- Ranks/positions are stored in the "api_rank" table with columns "code" (e.g. "DR-3.000") and "name" (e.g. "Able Seaman (AB)").
- CV submissions are in "api_cvsubmission" with a "position_id" FK pointing to "api_rank.id".
  This is the PRIMARY way to find which seafarers hold which position/rank.
- To find seafarers by position NAME (e.g. "Assistant Electrician", "Able Seaman (AB)"):
  SELECT COUNT(*) FROM api_cvsubmission cv JOIN api_rank r ON cv.position_id = r.id WHERE r.name = 'Assistant Electrician'
- To find seafarers by rank CODE (e.g. "DR-3.000", "ER-14.000"):
  SELECT COUNT(*) FROM api_cvsubmission cv JOIN api_rank r ON cv.position_id = r.id WHERE r.code = 'DR-3.000'
- To list seafarers with their position:
  SELECT u.first_name, u.middle_name, u.email, r.name as position FROM api_cvsubmission cv JOIN api_users u ON cv.user_id = u.id JOIN api_rank r ON cv.position_id = r.id
- Companies are in "companies_company" table.
- Sea service records are in "api_seaservice" table.
- Marine courses are in "courses_course" table.
- Ships are in "ships_ship" table.

Database Schema:
{schema}
"""

SYNTHESIS_PROMPT = """You are a helpful AI assistant.
Your task is to answer the user's question based on the provided database query results.
Provide a clear, natural language answer. If the results are empty, state that you couldn't find any data matching the criteria.

User Question: {question}

Database Query Results (JSON format, with columns and rows):
{results}
"""

def generate_sql(user_question: str) -> str:
    """LLM Call 1: Generate SQL query from natural language"""
    schema = get_abbreviated_schema()
    system_msg = SystemMessage(content=SQL_GENERATION_PROMPT.format(schema=schema))
    human_msg = HumanMessage(content=f"User Question: {user_question}")
    
    response = model.invoke([system_msg, human_msg])
    raw_response = response.content.strip()
    
    # Extract SQL if the model includes conversational text
    match = re.search(r"```(?:sql)?\s*(.*?)\s*```", raw_response, re.DOTALL | re.IGNORECASE)
    if match:
        sql_query = match.group(1).strip()
    else:
        # Fallback: Find the first SELECT
        upper_resp = raw_response.upper()
        if "SELECT" in upper_resp:
            start_idx = upper_resp.find("SELECT")
            sql_query = raw_response[start_idx:].strip()
        else:
            sql_query = raw_response
            
    return sql_query

def summarize_results(user_question: str, sql_results: dict) -> str:
    """LLM Call 2: Generate natural language response from SQL results"""
    results_str = json.dumps(sql_results, default=str)
    system_msg = SystemMessage(content=SYNTHESIS_PROMPT.format(question=user_question, results=results_str))
    human_msg = HumanMessage(content="Please provide the final answer.")
    
    response = model.invoke([system_msg, human_msg])
    return response.content.strip()

def process_database_question(user_question: str) -> str:
    """
    Main entrypoint for Text-to-SQL RAG.
    Implements Caching, Prompt Chaining, and Feedback Loop.
    """
    # 1. Caching (Check for existing answer)
    cache_entry = QueryCache.objects.filter(question__iexact=user_question).first()
    if cache_entry and cache_entry.final_answer:
        return cache_entry.final_answer

    # 2. SQL Generation
    sql_query = ""
    if cache_entry and cache_entry.sql_query:
        sql_query = cache_entry.sql_query
    else:
        try:
            sql_query = generate_sql(user_question)
        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            return "I'm sorry, I couldn't formulate a query to answer your question."

    # 3. Database Execution & Feedback Loop
    try:
        sql_results = execute_read_only_query(sql_query)
        
        # Save to cache if new
        if not cache_entry:
            cache_entry = QueryCache.objects.create(question=user_question, sql_query=sql_query)
            
    except Exception as e:
        # Feedback Loop: Log failed queries
        FailedQueryLog.objects.create(
            question=user_question,
            generated_sql=sql_query,
            error_message=str(e)
        )
        logger.error(f"SQL Execution Error: {str(e)} | Query: {sql_query}")
        return "I'm sorry, I encountered an error while trying to fetch the data."

    # 4. Final Synthesis
    try:
        final_answer = summarize_results(user_question, sql_results)
        
        # Update cache with final answer
        if cache_entry:
            cache_entry.final_answer = final_answer
            cache_entry.save()
            
        return final_answer
        
    except Exception as e:
        logger.error(f"Error synthesizing response: {str(e)}")
        return "I found the data, but encountered an error while trying to summarize it."
