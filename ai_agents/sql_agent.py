import json
import logging
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from .db_utils import get_abbreviated_schema, execute_read_only_query
from .models import QueryCache, FailedQueryLog
import os

logger = logging.getLogger(__name__)

def extract_text(response_content):
    if isinstance(response_content, str):
        return response_content.strip()
    elif isinstance(response_content, list):
        text_parts = []
        for part in response_content:
            if isinstance(part, dict) and 'text' in part:
                text_parts.append(part['text'])
            elif isinstance(part, str):
                text_parts.append(part)
        return " ".join(text_parts).strip()
    return str(response_content).strip()

# Use the same model as in agent.py
model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", google_api_key=os.environ.get("GOOGLE_API_KEY", "missing_key_please_add_to_env"))

# ─────────────────────────────────────────────────────────────────────
# INTENT DETECTION — decide whether the question is about a specific
# person (→ full-profile lookup) or aggregate data (→ SQL generation)
# ─────────────────────────────────────────────────────────────────────

INTENT_PROMPT = """You are a routing assistant for a maritime manning agency system.
Given the user's question, determine the intent:

1. "applicant_lookup" — The user is asking about a SPECIFIC person/applicant by name.
   Examples: "tell me about Ahmed Mohamed", "what ships did John work on?", "show me the profile of Captain Ali"
2. "monthly_stats" — The user is asking for monthly statistics, monthly report, dashboard overview or system-wide stats.
   Examples: "Get statistics for this month", "show me monthly statistics", "dashboard report for this month"
3. "endpoint_query" — The user is asking ANY other data question: listing companies, showing open jobs, finding contracts, searching CVs, filtering seafarers, checking documents, etc.
   Examples: "list active companies", "what are the open jobs?", "show upcoming interviews", "how many pending CVs?", "list Egyptian crew members"

Return ONLY one of these three words: applicant_lookup OR monthly_stats OR endpoint_query
Nothing else."""


def detect_intent(question: str) -> str:
    """Classify the user's question into an intent."""
    try:
        response = model.invoke([
            SystemMessage(content=INTENT_PROMPT),
            HumanMessage(content=question)
        ])
        intent_text = extract_text(response.content)
        intent = intent_text.lower().replace('"', '').replace("'", "")
        if "applicant_lookup" in intent:
            return "applicant_lookup"
        if "monthly_stats" in intent:
            return "monthly_stats"
        return "endpoint_query"  # default to endpoint query
    except Exception as e:
        logger.error(f"Intent detection error: {e}")
        return "endpoint_query"  # default fallback


# ─────────────────────────────────────────────────────────────────────
# APPLICANT NAME EXTRACTION
# ─────────────────────────────────────────────────────────────────────

NAME_EXTRACTION_PROMPT = """Extract the person's name from the user's question.
Return ONLY the name, nothing else. If multiple names are mentioned, return the primary one being asked about.

Examples:
- "tell me about Ahmed Mohamed" → Ahmed Mohamed
- "what ships did Captain Ali Hassan work on?" → Ali Hassan
- "show profile of AYMAN MOHAMED REFAAT RAMADAN" → AYMAN MOHAMED REFAAT RAMADAN
"""


def extract_applicant_name(question: str) -> str:
    """Extract the applicant name from the user's question."""
    try:
        response = model.invoke([
            SystemMessage(content=NAME_EXTRACTION_PROMPT),
            HumanMessage(content=question)
        ])
        return extract_text(response.content)
    except Exception as e:
        logger.error(f"Name extraction error: {e}")
        return ""


# ─────────────────────────────────────────────────────────────────────
# COMPANY NAME EXTRACTION
# ─────────────────────────────────────────────────────────────────────

COMPANY_NAME_EXTRACTION_PROMPT = """Extract the company name from the user's question.
Return ONLY the name, nothing else. Remove words like "company", "ltd", "inc" if they are just descriptive in the sentence, but keep the core name.

Examples:
- "tell me all about (3 SEAS) company" → 3 SEAS
- "what is the contact info for MSC?" → MSC
- "show me details for Maersk Shipping" → Maersk Shipping
"""

def extract_company_name(question: str) -> str:
    """Extract the company name from the user's question."""
    try:
        response = model.invoke([
            SystemMessage(content=COMPANY_NAME_EXTRACTION_PROMPT),
            HumanMessage(content=question)
        ])
        return extract_text(response.content)
    except Exception as e:
        logger.error(f"Name extraction error: {e}")
        return ""


# ─────────────────────────────────────────────────────────────────────
# FULL PROFILE LOOKUP — uses the same data as /api/users/{id}/full-profile/
# ─────────────────────────────────────────────────────────────────────

def lookup_applicant_profile(name: str) -> dict:
    """
    Search for an applicant by name and return their full profile data.
    Uses the same serializers as GET /api/users/{id}/full-profile/
    """
    from django.db.models import Q, Value
    from django.db.models.functions import Concat
    from api.models import Users, Contract
    from api.serializer import UsersSerializer, ContractListSerializer

    # Annotate with full name for easier searching
    users = Users.objects.annotate(
        full_name=Concat('first_name', Value(' '), 'middle_name')
    )

    # 1. Try exact match (case-insensitive)
    exact_matches = users.filter(full_name__icontains=name)
    if exact_matches.exists():
        users = exact_matches
    else:
        # 2. Try matching all terms anywhere in the name
        terms = name.strip().split()
        query = Q()
        for term in terms:
            query &= Q(full_name__icontains=term)
        users = users.filter(query)

    if not users.exists():
        return {"error": f"No applicant found matching the name '{name}'."}

    # If multiple matches, pick the best one (or return them all if <= 3)
    if users.count() > 3:
        # Too many matches — return a list of names for the user to choose from
        matches = [
            {"id": u.id, "name": f"{u.first_name} {u.middle_name}".strip(), "email": u.email}
            for u in users[:10]
        ]
        return {
            "multiple_matches": True,
            "count": users.count(),
            "matches": matches,
            "message": f"Found {users.count()} applicants matching '{name}'. Here are the top results:"
        }

    # Get the best match (first result)
    user = users.first()

    # Use the same serializer as the full-profile endpoint
    user_data = UsersSerializer(user).data

    # Add contracts (same as full-profile endpoint)
    contracts = Contract.objects.filter(user=user).select_related('ship', 'company', 'rank')
    user_data['contracts'] = ContractListSerializer(contracts, many=True).data

    return user_data


# ─────────────────────────────────────────────────────────────────────
# PROFILE SUMMARIZATION — LLM generates a human-friendly answer
# ─────────────────────────────────────────────────────────────────────

PROFILE_SUMMARY_PROMPT = """You are a helpful AI assistant for a maritime manning agency.
You have been given the complete profile data of an applicant/seafarer.
Answer the user's question based on this profile data.
Be thorough and provide all relevant details from the profile.
Format your response clearly with sections if needed.

If the user asked a general question like "tell me about this applicant", provide a comprehensive summary including:
- Personal info (name, nationality, date of birth, contact info)
- Applied position and rank codes
- Sea service history (ships, ranks, dates)
- Documents status (passport, seaman book, COC, GOC, expiry dates)
- Marine courses
- Contracts (companies and ships signed on)
- Any other relevant information

User Question: {question}

Applicant Profile Data:
{profile_data}
"""


def summarize_profile(question: str, profile_data: dict) -> str:
    """Use the LLM to generate a human-friendly summary of the profile."""
    # Trim large nested structures to avoid context explosion
    trimmed = {k: v for k, v in profile_data.items()}

    # Keep seafarer_application compact
    if 'seafarer_application' in trimmed:
        trimmed['seafarer_application'] = "[Full application form data available]"

    profile_str = json.dumps(trimmed, default=str, indent=2)

    # Truncate if too large (keep under ~30k chars for the LLM)
    if len(profile_str) > 30000:
        profile_str = profile_str[:30000] + "\n... [truncated]"

    response = model.invoke([
        SystemMessage(content=PROFILE_SUMMARY_PROMPT.format(
            question=question, profile_data=profile_str
        )),
        HumanMessage(content="Please provide the answer based on the profile data above.")
    ])
    return extract_text(response.content)


# ─────────────────────────────────────────────────────────────────────
# COMPANY PROFILE LOOKUP
# ─────────────────────────────────────────────────────────────────────

def lookup_company_profile(name: str) -> dict:
    """Search for a company by name and return its details."""
    from django.db.models import Q
    from companies.models import Company
    from companies.serializers import CompanySerializer

    name = name.strip()
    
    # Try exact match first
    companies = Company.objects.filter(company_name__iexact=name)
    
    # Try partial match if no exact match
    if not companies.exists():
        companies = Company.objects.filter(company_name__icontains=name)

    if not companies.exists():
        return {"error": f"No company found matching the name '{name}'."}

    # If multiple matches, pick the best one (or return them all if <= 3)
    if companies.count() > 3:
        matches = [
            {"id": c.id, "name": c.company_name, "email": c.contact_email}
            for c in companies[:10]
        ]
        return {
            "multiple_matches": True,
            "count": companies.count(),
            "matches": matches,
            "message": f"Found {companies.count()} companies matching '{name}'. Here are the top results:"
        }

    company = companies.first()
    return CompanySerializer(company).data


COMPANY_SUMMARY_PROMPT = """You are a helpful AI assistant for a maritime manning agency.
You have been given the profile data of a company that the agency works with.
Answer the user's question based on this profile data.
Be thorough and provide all relevant details from the profile.

If the user asked a general question like "tell me about this company", provide a comprehensive summary including:
- Company name and type
- Contact information (email, phone, website)
- Address and country
- Contact persons and their info
- Status and open positions
- Any notes

User Question: {question}

Company Profile Data:
{profile_data}
"""

def summarize_company(question: str, profile_data: dict) -> str:
    """Use the LLM to generate a human-friendly summary of the company."""
    profile_str = json.dumps(profile_data, default=str, indent=2)

    response = model.invoke([
        SystemMessage(content=COMPANY_SUMMARY_PROMPT.format(
            question=question, profile_data=profile_str
        )),
        HumanMessage(content="Please provide the answer based on the company data above.")
    ])
    return extract_text(response.content)



# ─────────────────────────────────────────────────────────────────────
# OPEN JOBS LOOKUP
# ─────────────────────────────────────────────────────────────────────

def lookup_open_jobs() -> list:
    """Fetch currently open and active job orders."""
    from companies.models import JobOrder
    from companies.serializers import JobOrderSerializer

    # Fetch job orders that are currently open/active/in progress
    job_orders = JobOrder.objects.filter(
        status__in=['Open', 'Active', 'Pending', 'In Progress']
    ).prefetch_related('positions', 'positions__rank', 'company', 'ship').order_by('-request_date')

    if not job_orders.exists():
        return []

    # Serialize up to 20 recent job orders to avoid token limits
    return JobOrderSerializer(job_orders[:20], many=True).data

OPEN_JOBS_SUMMARY_PROMPT = """You are a helpful AI assistant for a maritime manning agency.
The user is asking about open jobs or vacancies. 
You have been given a list of currently open 'Job Orders' and the specific 'Positions' (ranks) required for each.
Summarize the available jobs clearly for the user. Group them by company or vessel if it makes sense.
Be sure to mention the ranks needed, quantities, and any salary/duration information if available.
If the list of jobs is empty, politely inform the user that there are currently no open jobs.

User Question: {question}

Open Jobs Data:
{jobs_data}
"""

def summarize_open_jobs(question: str, jobs_data: list) -> str:
    """Use the LLM to generate a summary of open jobs."""
    if not jobs_data:
        return 'There are currently no open jobs or vacancies available at this time.'
        
    import json
    jobs_str = json.dumps(jobs_data, default=str, indent=2)

    response = model.invoke([
        SystemMessage(content=OPEN_JOBS_SUMMARY_PROMPT.format(
            question=question, jobs_data=jobs_str
        )),
        HumanMessage(content='Please provide the summary of open jobs based on the data above.')
    ])
    return extract_text(response.content)


# ─────────────────────────────────────────────────────────────────────
# LIST COMPANIES
# ─────────────────────────────────────────────────────────────────────

def get_companies_list(status_filter=None) -> list:
    """Fetch a list of companies, optionally filtered by status."""
    from companies.models import Company
    
    qs = Company.objects.all().order_by('company_name')
    if status_filter:
        qs = qs.filter(status__iexact=status_filter)
        
    return list(qs.values('id', 'company_name', 'status', 'contact_email', 'open_positions'))

LIST_COMPANIES_SUMMARY_PROMPT = """You are a helpful AI assistant for a maritime manning agency.
The user is asking for a list of companies (possibly filtered, e.g., active companies).
You have been given a JSON list of companies. Summarize the list clearly for the user.
If there are many companies, you can list the names and mention their statuses or open positions briefly.
If the list is empty, politely inform the user that no companies match the criteria.

User Question: {question}

Companies Data:
{companies_data}
"""

def summarize_companies_list(question: str, companies_data: list) -> str:
    import json
    if not companies_data:
        return 'There are currently no companies found.'
        
    data_str = json.dumps(companies_data, default=str, indent=2)
    response = model.invoke([
        SystemMessage(content=LIST_COMPANIES_SUMMARY_PROMPT.format(
            question=question, companies_data=data_str
        )),
        HumanMessage(content='Please provide the list of companies based on the data above.')
    ])
    return extract_text(response.content)


# ─────────────────────────────────────────────────────────────────────
# MONTHLY / SYSTEM STATISTICS
# ─────────────────────────────────────────────────────────────────────

def get_all_system_stats(year: int, month: int) -> dict:
    """Query all statistics from core models for the given month and overall."""
    from django.utils import timezone
    from api.models import Users, Contract, Interview, CVSubmission, Document
    from companies.models import Company
    from finance.models import FinanceRecord
    from datetime import timedelta
    
    today = timezone.now().date()
    
    # 1. User stats
    users = Users.objects.all()
    overall_users = {
        'total_users': users.count(),
        'admins': users.filter(role='Admin').count(),
        'hr_managers': users.filter(role='HR Manager').count(),
        'recruiters': users.filter(role='Recruiter').count(),
        'employees': users.filter(role='Employee').count(),
        'active_users': users.filter(is_active=True).count(),
    }
    monthly_users = users.filter(created_at__year=year, created_at__month=month).count()
    
    # 2. Contract stats
    contracts = Contract.objects.all()
    overall_contracts = {
        'signed_contracts': contracts.filter(status='Signed').count(),
        'pending_signature': contracts.filter(status='Pending Signature').count(),
        'drafts': contracts.filter(status='Draft').count(),
        'active': contracts.filter(status='Active').count(),
        'completed': contracts.filter(status='Completed').count(),
        'pending': contracts.filter(status='Pending').count(),
    }
    monthly_contracts = contracts.filter(created_at__year=year, created_at__month=month).count()
    
    # 3. Company stats
    companies = Company.objects.all()
    overall_companies = {
        'total_companies': companies.count(),
        'active_companies': companies.filter(status='Active').count(),
        'prospect_companies': companies.filter(status='Prospect').count(),
        'inactive_companies': companies.filter(status='Inactive').count(),
    }
    monthly_companies = companies.filter(created_at__year=year, created_at__month=month).count()
    
    # 4. Interview stats
    interviews = Interview.objects.all()
    overall_interviews = {
        'total_interviews': interviews.count(),
        'today_interviews': interviews.filter(scheduled_date=today).count(),
        'pending_confirmation': interviews.filter(status='Pending Confirmation').count(),
        'scheduled': interviews.filter(status='Scheduled').count(),
        'completed': interviews.filter(status='Completed').count(),
    }
    monthly_interviews = interviews.filter(scheduled_date__year=year, scheduled_date__month=month).count()
    
    # 5. CV Submission stats
    cvs = CVSubmission.objects.all()
    overall_cvs = {
        'total_cvs': cvs.count(),
        'under_review': cvs.filter(status='Under Review').count(),
        'interviewed': cvs.filter(status='Interviewed').count(),
        'pending': cvs.filter(status='Pending').count(),
        'approved': cvs.filter(status='Approved').count(),
    }
    monthly_cvs = cvs.filter(submitted_date__year=year, submitted_date__month=month).count()
    
    # 6. Finance stats
    finance = FinanceRecord.objects.all()
    overall_finance = {
        'total_records': finance.count(),
        'pending': finance.filter(status='Pending').count(),
        'paid': finance.filter(status='Paid').count(),
    }
    monthly_finance = finance.filter(created_at__year=year, created_at__month=month).count()
    
    # 7. Document stats
    docs = Document.objects.all()
    overall_docs = {
        'total_documents': docs.count(),
        'pending': docs.filter(status='Pending').count(),
        'active': docs.filter(status='Active').count(),
        'blacklist': docs.filter(status='Blacklist').count(),
    }
    monthly_docs = docs.filter(created_at__year=year, created_at__month=month).count()
    
    return {
        "period": f"{year}-{month:02d}",
        "overall_cumulative_statistics": {
            "users": overall_users,
            "contracts": overall_contracts,
            "companies": overall_companies,
            "interviews": overall_interviews,
            "cv_submissions": overall_cvs,
            "finance_records": overall_finance,
            "documents": overall_docs
        },
        "this_month_statistics": {
            "new_users_registered": monthly_users,
            "contracts_created": monthly_contracts,
            "companies_added": monthly_companies,
            "interviews_scheduled": monthly_interviews,
            "cv_submissions_received": monthly_cvs,
            "finance_records_created": monthly_finance,
            "documents_uploaded": monthly_docs
        }
    }

MONTHLY_STATS_PROMPT = """You are a helpful AI assistant for a maritime manning agency.
The user is asking for monthly statistics, reports, or a general system stats summary.
You have been given a JSON payload containing the overall cumulative statistics (from the stats endpoints) and statistics specifically for the requested month.

Present the statistics clearly, professionally, and in a structured, readable way (e.g. using bullet points, tables, or markdown formatting).
Highlight important figures such as new registered users, signed/active contracts, upcoming interviews, new CV submissions, etc. for the requested month.

User Question: {question}

System Statistics Data:
{stats_data}
"""

def summarize_monthly_stats(question: str, stats_data: dict) -> str:
    """Use LLM to summarize system statistics."""
    import json
    data_str = json.dumps(stats_data, default=str, indent=2)
    response = model.invoke([
        SystemMessage(content=MONTHLY_STATS_PROMPT.format(
            question=question, stats_data=data_str
        )),
        HumanMessage(content='Please summarize the statistics above.')
    ])
    return extract_text(response.content)

def _handle_monthly_stats(user_question: str) -> str:
    """Retrieve and summarize system statistics for the current month."""
    try:
        from django.utils import timezone
        now = timezone.now()
        # Heuristic to parse month/year or fallback to current
        year = now.year
        month = now.month
        
        # Simple extraction of month names if mentioned
        q_lower = user_question.lower()
        months_map = {
            'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6,
            'july': 7, 'august': 8, 'september': 9, 'october': 10, 'november': 11, 'december': 12
        }
        for name, num in months_map.items():
            if name in q_lower:
                month = num
                break
                
        logger.info(f"Fetching monthly stats for {year}-{month:02d}")
        stats_data = get_all_system_stats(year, month)
        return summarize_monthly_stats(user_question, stats_data)
    except Exception as e:
        logger.error(f"Monthly stats error: {e}", exc_info=True)
        return f"I encountered an error while fetching the statistics. Error: {str(e)}"

# ─────────────────────────────────────────────────────────────────────
# TEXT-TO-SQL (kept for aggregate queries)



# ─────────────────────────────────────────────────────────────────────

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
- Contracts are in "api_contract" table with FK to api_users (user_id), ships_ship (ship_id), companies_company (company_id).
- User status field is "user_status" on api_users. Common values: ON_SITE, AVAILABLE, ON_BOARD.

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
    raw_response = extract_text(response.content)
    
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
    
    # Strip trailing semicolons and extra whitespace
    sql_query = sql_query.rstrip(';').strip()
    
    return sql_query

def summarize_results(user_question: str, sql_results: dict) -> str:
    """LLM Call 2: Generate natural language response from SQL results"""
    results_str = json.dumps(sql_results, default=str)
    system_msg = SystemMessage(content=SYNTHESIS_PROMPT.format(question=user_question, results=results_str))
    human_msg = HumanMessage(content="Please provide the final answer.")
    
    response = model.invoke([system_msg, human_msg])
    return extract_text(response.content)


# ─────────────────────────────────────────────────────────────────────
# MAIN ENTRYPOINT
# ─────────────────────────────────────────────────────────────────────

def process_database_question(user_question: str) -> str:
    """
    Main entrypoint — routes to either:
    1. Full-profile lookup (for questions about specific applicants)
    2. Text-to-SQL RAG (for aggregate/general database questions)
    """
    # Intent Detection — is the user asking about a specific person, company, jobs or listing?
    intent = detect_intent(user_question)
    logger.info(f"Intent detected: {intent} for question: {user_question}")

    if intent == "applicant_lookup":
        return _handle_applicant_lookup(user_question)
    elif intent == "monthly_stats":
        return _handle_monthly_stats(user_question)
    else:
        return _handle_endpoint_query(user_question)

def _handle_list_companies(user_question: str) -> str:
    """Handle requests to list companies."""
    try:
        logger.info("Listing companies")
        
        # Simple heuristic to determine if user asked for "active" companies
        status_filter = 'Active' if 'active' in user_question.lower() else None
        
        companies_data = get_companies_list(status_filter)
        answer = summarize_companies_list(user_question, companies_data)

        return answer
    except Exception as e:
        logger.error(f"List companies error: {e}", exc_info=True)
        return f"I encountered an error while retrieving the list of companies. Error: {str(e)}"

def _handle_open_jobs_lookup(user_question: str) -> str:
    """Handle questions about open jobs and vacancies."""
    try:
        logger.info("Looking up open jobs")
        jobs_data = lookup_open_jobs()
        answer = summarize_open_jobs(user_question, jobs_data)

        return answer
    except Exception as e:
        logger.error(f"Open jobs lookup error: {e}", exc_info=True)
        return f"I encountered an error while retrieving open jobs. Error: {str(e)}"

def _handle_company_lookup(user_question: str) -> str:
    """Handle questions about specific companies."""
    try:
        name = extract_company_name(user_question)
        if not name:
            return "I couldn't identify the company name from your question."

        logger.info(f"Looking up company: {name}")

        profile_data = lookup_company_profile(name)

        if profile_data.get("multiple_matches"):
            matches_text = "\n".join(
                [f"  - {m['name']} (ID: {m['id']}, Email: {m['email']})" for m in profile_data['matches']]
            )
            return f"{profile_data['message']}\n\n{matches_text}\n\nPlease specify the exact company name."

        if profile_data.get("error"):
            return profile_data["error"]

        answer = summarize_company(user_question, profile_data)

        return answer

    except Exception as e:
        logger.error(f"Company lookup error: {e}", exc_info=True)
        return f"I encountered an error while looking up the company. Error: {str(e)}"

def _handle_applicant_lookup(user_question: str) -> str:
    """Handle questions about specific applicants using the full-profile data."""
    try:
        # Extract the applicant name from the question
        name = extract_applicant_name(user_question)
        if not name:
            return "I couldn't identify the applicant name from your question. Could you please provide the full name?"

        logger.info(f"Looking up applicant: {name}")

        # Fetch the full profile
        profile_data = lookup_applicant_profile(name)

        # Handle multiple matches
        if profile_data.get("multiple_matches"):
            matches_text = "\n".join(
                [f"  - {m['name']} (ID: {m['id']}, Email: {m['email']})" for m in profile_data['matches']]
            )
            return f"{profile_data['message']}\n\n{matches_text}\n\nPlease specify the exact name to get the full profile."

        # Handle no matches
        if profile_data.get("error"):
            return profile_data["error"]

        # Summarize the profile with the LLM
        answer = summarize_profile(user_question, profile_data)

        return answer

    except Exception as e:
        logger.error(f"Applicant lookup error: {e}", exc_info=True)
        return f"I encountered an error while looking up the applicant. Error: {str(e)}"


def _handle_endpoint_query(user_question: str) -> str:
    """Handle general queries using the endpoint-aware filter engine."""
    from .endpoint_query_engine import plan_query, execute_query, summarize_query_results

    try:
        # Step 1: Plan the query (LLM picks endpoint + filters)
        plan = plan_query(user_question, model)
        if not plan:
            logger.warning("Endpoint query planner returned None, falling back to Text-to-SQL")
            return _handle_sql_fallback(user_question)

        logger.info(f"Query plan: endpoint={plan.get('endpoint')}, filters={plan.get('filters')}")

        # Step 2: Execute the ORM query
        result = execute_query(plan)
        result["hint"] = plan.get("hint", "")

        # Step 3: Summarize the results
        return summarize_query_results(user_question, result, model)

    except Exception as e:
        logger.error(f"Endpoint query error: {e}", exc_info=True)
        # Fallback to Text-to-SQL if the endpoint engine fails
        logger.info("Falling back to Text-to-SQL")
        return _handle_sql_fallback(user_question)


def _handle_sql_fallback(user_question: str) -> str:
    """Fallback: use Text-to-SQL for queries the endpoint engine can't handle."""
    try:
        sql_query = generate_sql(user_question)
        sql_results = execute_read_only_query(sql_query)
        return summarize_results(user_question, sql_results)
    except Exception as e:
        logger.error(f"SQL fallback also failed: {e}")
        FailedQueryLog.objects.create(
            question=user_question,
            generated_sql=str(e),
            error_message=str(e)
        )
        return "I'm sorry, I encountered an error while trying to fetch the data. Please try rephrasing your question."
