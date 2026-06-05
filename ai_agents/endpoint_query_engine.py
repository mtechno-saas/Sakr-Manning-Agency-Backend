"""
Endpoint-Aware Query Engine
============================
Replaces fragile Text-to-SQL with structured ORM filter queries.
The LLM selects an endpoint and extracts filter parameters,
then Django ORM executes the query safely and accurately.
"""
import json
import logging
import re
from datetime import datetime, timedelta
from django.utils import timezone
from langchain_core.messages import HumanMessage, SystemMessage

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────
# ENDPOINTS REFERENCE (fed to the LLM for query planning)
# ─────────────────────────────────────────────────────────────────────

ENDPOINTS_REFERENCE = """
### 1. users — Seafarers / Applicants / Crew
Filters: name (str), nationality (str), user_status (str: ON_SITE|VACATION|ON_BOARD|AVAILABLE),
role (str: Admin|HR Manager|Recruiter|Employee), is_blacklisted (bool),
position (str - matches application_for_position), rank_name (str),
company_name (str), ship_name (str), passport_no (str), seaman_book_no (str),
course_name (str), document_status (str: Pending|Active|Blacklist)

### 2. companies — Companies / Clients
Filters: name (str), status (str: Active|Inactive|Prospect), company_type (str)

### 3. ships — Vessels / Ships
Filters: name (str), imo_number (str), status (str), flag (str), ship_type (str)

### 4. job_orders — Job Orders / Vacancies
Filters: status (str: Open|Pending|Active|In Progress|Fulfilled|Cancelled),
request_date_from (date), request_date_to (date)

### 5. cv_submissions — CV Submissions / Applications
Filters: status (str: Pending|Under Review|Interviewed|Approved|Rejected|Hired),
submitted_date_from (date), submitted_date_to (date)

### 6. interviews — Interviews / Scheduling
Filters: status (str: Scheduled|Completed|Cancelled|Rescheduled|No Show),
scheduled_date (date), scheduled_date_from (date), scheduled_date_to (date),
interview_type (str: Phone|Video|In-Person|Technical)

### 7. contracts — Contracts / Assignments
Filters: status (str: Active|Completed|Pending|Signed|Pending Signature|Draft|Cancelled),
applicant_name (str), sign_on_from (date), sign_on_to (date),
sign_off_from (date), sign_off_to (date)

### 8. finance — Finance Records
Filters: status (str: Pending|Paid|Overdue|Cancelled),
start_date_from (date), start_date_to (date)

### 9. documents — Quick Apply Documents
Filters: status (str: Pending|Active|Blacklist), name (str), position (str)
"""

QUERY_PLANNER_PROMPT = """You are a query planner for a maritime manning agency backend.
Given the user's question, select the best API endpoint and extract filter parameters.

Today's date: {today}  |  Current month: {month_name} {year}

{endpoints_ref}

Return ONLY a valid JSON object — no markdown, no backticks, no explanation:
{{
  "endpoint": "users|companies|ships|job_orders|cv_submissions|interviews|contracts|finance|documents",
  "filters": {{"filter_name": "value"}},
  "count_only": false,
  "limit": 20,
  "hint": "what the user wants in a few words"
}}

Rules:
- Dates must be ISO format YYYY-MM-DD.
- "this week" → scheduled_date_from={today}, scheduled_date_to={week_end}
- "this month" → use _from with first day and _to with last day of current month.
- "today" → use exact date {today}.
- count_only=true ONLY if the user asks "how many" / "count".
- "seafarers"/"applicants"/"crew" → users endpoint.
- "vacancies"/"open positions" → job_orders endpoint.
- limit defaults to 20, max 50 for broad listings.
"""

RESULTS_SUMMARY_PROMPT = """You are a helpful AI assistant for a maritime manning agency.
Summarize the following query results clearly for the user.
If the data is a list, present it in a readable format.
If count_only is true, state the count clearly.
If results are empty, say no matching records were found.

User Question: {question}
Query Hint: {hint}
Total Matching Records: {total}
Data (JSON):
{data}
"""


# ─────────────────────────────────────────────────────────────────────
# QUERY PLANNER — LLM decides endpoint + filters
# ─────────────────────────────────────────────────────────────────────

def plan_query(question: str, model) -> dict:
    """Ask the LLM to pick an endpoint and extract filters."""
    today = timezone.now().date()
    week_end = today + timedelta(days=7)
    month_name = today.strftime("%B")

    prompt = QUERY_PLANNER_PROMPT.format(
        today=today.isoformat(),
        week_end=week_end.isoformat(),
        month_name=month_name,
        year=today.year,
        endpoints_ref=ENDPOINTS_REFERENCE,
    )

    from .sql_agent import extract_text
    response = model.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=question),
    ])
    raw = extract_text(response.content)

    # Parse JSON from the response
    # Try to find JSON object in the response
    json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', raw, re.DOTALL)
    if json_match:
        raw = json_match.group(0)

    try:
        plan = json.loads(raw)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse query plan JSON: {raw}")
        return None

    # Validate
    valid_endpoints = [
        "users", "companies", "ships", "job_orders",
        "cv_submissions", "interviews", "contracts", "finance", "documents",
    ]
    if plan.get("endpoint") not in valid_endpoints:
        logger.error(f"Invalid endpoint in plan: {plan.get('endpoint')}")
        return None

    return plan


# ─────────────────────────────────────────────────────────────────────
# QUERY EXECUTOR — builds Django ORM queries from the plan
# ─────────────────────────────────────────────────────────────────────

# Mapping: filter_name → ORM lookup expression
FILTER_MAPS = {
    "users": {
        "name":             "first_name__icontains",
        "nationality":      "nationality__icontains",
        "user_status":      "user_status",
        "role":             "role",
        "is_blacklisted":   "is_blacklisted",
        "position":         "application_for_position__icontains",
        "rank_name":        "ranks__rank__name__icontains",
        "company_name":     "contracts__company__company_name__icontains",
        "ship_name":        "contracts__ship__ship_name__icontains",
        "passport_no":      "passport_no__icontains",
        "seaman_book_no":   "seaman_book_no__icontains",
        "course_name":      "courses__course_name__icontains",
        "document_status":  "documents__status__iexact",
    },
    "companies": {
        "name":         "company_name__icontains",
        "status":       "status",
        "company_type": "company_type__icontains",
    },
    "ships": {
        "name":       "ship_name__icontains",
        "imo_number": "imo_number__icontains",
        "status":     "status",
        "flag":       "flag__name__icontains",
        "ship_type":  "ship_type__name__icontains",
    },
    "job_orders": {
        "status":            "status",
        "request_date_from": "request_date__gte",
        "request_date_to":   "request_date__lte",
    },
    "cv_submissions": {
        "status":              "status__iexact",
        "submitted_date_from": "submitted_date__gte",
        "submitted_date_to":   "submitted_date__lte",
    },
    "interviews": {
        "status":              "status__iexact",
        "scheduled_date":      "scheduled_date",
        "scheduled_date_from": "scheduled_date__gte",
        "scheduled_date_to":   "scheduled_date__lte",
        "interview_type":      "interview_type__iexact",
    },
    "contracts": {
        "status":         "status",
        "applicant_name": "user__first_name__icontains",
        "sign_on_from":   "sign_on_date__gte",
        "sign_on_to":     "sign_on_date__lte",
        "sign_off_from":  "sign_off_date__gte",
        "sign_off_to":    "sign_off_date__lte",
    },
    "finance": {
        "status":          "status__iexact",
        "start_date_from": "start_date__gte",
        "start_date_to":   "start_date__lte",
    },
    "documents": {
        "status":   "status__iexact",
        "name":     "name__icontains",
        "position": "position__icontains",
    },
}

# Fields to return for each endpoint (lightweight .values() output)
DISPLAY_FIELDS = {
    "users": [
        "id", "first_name", "email", "nationality",
        "application_for_position", "user_status", "phone_number",
        "available_date", "generated_id",
    ],
    "companies": [
        "id", "company_name", "status", "contact_email",
        "company_type", "open_positions",
    ],
    "ships": [
        "id", "ship_name", "imo_number", "status",
    ],
    "job_orders": [
        "id", "status", "request_date", "notes",
    ],
    "cv_submissions": [
        "id", "user__first_name", "user__email",
        "position__name", "status", "submitted_date",
    ],
    "interviews": [
        "id", "candidate__first_name", "candidate__email",
        "scheduled_date", "scheduled_time", "interview_type",
        "status", "result", "location",
    ],
    "contracts": [
        "id", "user__first_name", "user__email",
        "ship__ship_name", "company__company_name",
        "rank__name", "sign_on_date", "sign_off_date", "status",
    ],
    "finance": [
        "id", "user__first_name", "company__company_name",
        "status", "start_date", "end_date",
    ],
    "documents": [
        "id", "title", "name", "email", "position", "status", "created_at",
    ],
}


def _get_base_queryset(endpoint: str):
    """Import and return the base queryset for an endpoint."""
    if endpoint == "users":
        from api.models import Users
        return Users.objects.all().order_by("-created_at")
    elif endpoint == "companies":
        from companies.models import Company
        return Company.objects.all().order_by("company_name")
    elif endpoint == "ships":
        from ships.models import Ship
        return Ship.objects.all().order_by("ship_name")
    elif endpoint == "job_orders":
        from companies.models import JobOrder
        return JobOrder.objects.prefetch_related(
            "positions", "positions__rank", "company", "ship"
        ).all().order_by("-request_date")
    elif endpoint == "cv_submissions":
        from api.models import CVSubmission
        return CVSubmission.objects.select_related(
            "user", "position"
        ).all().order_by("-submitted_date")
    elif endpoint == "interviews":
        from api.models import Interview
        return Interview.objects.select_related(
            "candidate", "company", "position"
        ).all().order_by("-scheduled_date")
    elif endpoint == "contracts":
        from api.models import Contract
        return Contract.objects.select_related(
            "user", "ship", "company", "rank"
        ).all().order_by("-sign_on_date")
    elif endpoint == "finance":
        from finance.models import FinanceRecord
        return FinanceRecord.objects.select_related(
            "user", "company"
        ).all().order_by("-start_date")
    elif endpoint == "documents":
        from api.models import Document
        return Document.objects.all().order_by("-created_at")
    else:
        raise ValueError(f"Unknown endpoint: {endpoint}")


def _coerce_value(key: str, value):
    """Convert string values to the right Python types."""
    if key == "is_blacklisted":
        return str(value).lower() in ("true", "1", "yes")
    # Dates are passed as strings — Django handles ISO date strings fine
    return value


def execute_query(plan: dict) -> dict:
    """Execute the ORM query described by the plan and return results."""
    endpoint = plan["endpoint"]
    filters = plan.get("filters", {})
    count_only = plan.get("count_only", False)
    limit = min(plan.get("limit", 20), 50)

    qs = _get_base_queryset(endpoint)
    fmap = FILTER_MAPS.get(endpoint, {})

    # Apply each filter
    for param, value in filters.items():
        if param in fmap and value not in (None, "", "null"):
            lookup = fmap[param]
            qs = qs.filter(**{lookup: _coerce_value(param, value)})

    total = qs.count()

    if count_only:
        return {"endpoint": endpoint, "total": total, "count_only": True, "results": []}

    # For job_orders, use a richer serialization
    if endpoint == "job_orders":
        return _serialize_job_orders(qs, limit, total)

    # Generic: use .values()
    fields = DISPLAY_FIELDS.get(endpoint, ["id"])
    # Filter out fields that may not exist on the model
    try:
        results = list(qs.values(*fields)[:limit])
    except Exception:
        # Fallback if some FK fields don't exist
        results = list(qs.values("id")[:limit])

    return {"endpoint": endpoint, "total": total, "count_only": False, "results": results}


def _serialize_job_orders(qs, limit, total):
    """Serialize job orders with their nested positions."""
    results = []
    for jo in qs[:limit]:
        positions = []
        for pos in jo.positions.all():
            positions.append({
                "rank": pos.rank.name if pos.rank else "N/A",
                "quantity": pos.quantity,
                "salary_from": str(pos.salary_from) if pos.salary_from else None,
                "salary_to": str(pos.salary_to) if pos.salary_to else None,
                "duration_months": pos.duration_months,
            })
        results.append({
            "id": jo.id,
            "company": jo.company.company_name if jo.company else "N/A",
            "ship": jo.ship.ship_name if jo.ship else "N/A",
            "status": jo.status,
            "request_date": str(jo.request_date) if jo.request_date else None,
            "positions": positions,
            "notes": jo.notes or "",
        })
    return {"endpoint": "job_orders", "total": total, "count_only": False, "results": results}


# ─────────────────────────────────────────────────────────────────────
# RESULT SUMMARIZER
# ─────────────────────────────────────────────────────────────────────

def summarize_query_results(question: str, query_result: dict, model) -> str:
    """Use LLM to summarize the query results in natural language."""
    from .sql_agent import extract_text

    if query_result.get("count_only"):
        return f"There are **{query_result['total']}** matching records."

    if not query_result.get("results"):
        return "I couldn't find any records matching your criteria."

    data_str = json.dumps(query_result["results"], default=str, indent=2)
    # Truncate if too large to avoid token limits
    if len(data_str) > 12000:
        data_str = data_str[:12000] + "\n... (truncated)"

    prompt = RESULTS_SUMMARY_PROMPT.format(
        question=question,
        hint=query_result.get("hint", ""),
        total=query_result.get("total", len(query_result["results"])),
        data=data_str,
    )

    response = model.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content="Please summarize the results."),
    ])
    return extract_text(response.content)
