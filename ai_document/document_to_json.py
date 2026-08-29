import os
import re
import json
import time
import traceback
from typing import List, Optional, Any
from pydantic import BaseModel, Field

from django.conf import settings

# --- LLM ROUTER ---
def _get_active_llm(api_keys_config: dict):
    if isinstance(api_keys_config, str):
        try:
            api_keys_config = json.loads(api_keys_config)
            if isinstance(api_keys_config, str):
                api_keys_config = json.loads(api_keys_config)
        except Exception:
            api_keys_config = {}

    if not isinstance(api_keys_config, dict):
        api_keys_config = {}

    now = time.time()

    # 0. Try Ollama (local) — primary LLM fallback when configured.
    #    Free, private, no rate limit. Skipped when:
    #      * OLLAMA_ENABLED is false
    #      * api_keys_config contains a hard "ollama_disabled": true
    #    If the local server isn't running or the model isn't pulled,
    #    we fall through to DeepSeek (primary cloud LLM).
    if getattr(settings, "OLLAMA_ENABLED", True) and not api_keys_config.get("ollama_disabled"):
        ollama_host = getattr(settings, "OLLAMA_HOST", "") or os.environ.get("OLLAMA_HOST", "")
        ollama_model = (
            api_keys_config.get("ollama_model")
            or getattr(settings, "OLLAMA_MODEL", "qwen2.5:7b")
        )
        if ollama_host:
            try:
                from langchain_ollama import ChatOllama
                llm = ChatOllama(
                    model=ollama_model,
                    base_url=ollama_host,
                    temperature=0,
                    # JSON-mode: model is told to emit raw JSON only.
                    # qwen2.5+ / llama3.1+ / mistral-nemo all support this.
                    format="json",
                    timeout=getattr(settings, "OLLAMA_TIMEOUT_SECONDS", 60),
                )
                return llm, {
                    "provider": "ollama",
                    "model": ollama_model,
                    "host": ollama_host,
                }
            except Exception as e:
                # Most likely causes: ollama not running, model not pulled,
                # or langchain_ollama not installed. Log and fall through
                # to DeepSeek so the request still works.
                print(
                    f"[Ollama] init failed for {ollama_host} model={ollama_model}: "
                    f"{e!r} — falling through to DeepSeek"
                )

    # 1. Try DeepSeek (primary cloud LLM, OpenAI-compatible)
    #    Free tier has no daily token cap (unlike Groq's 200K TPD limit
    #    that bit us in production). Default model is `deepseek-chat` (V3).
    #    API key from https://platform.deepseek.com → API Keys.
    #    Disable per-request with api_keys_config["deepseek_disabled"] = True.
    if not api_keys_config.get("deepseek_disabled") and getattr(settings, "DEEPSEEK_ENABLED", True):
        deepseek_keys = api_keys_config.get("deepseek", [])
        if not deepseek_keys:
            # Check settings first (so override_settings works in tests),
            # then env as a fallback. In production these are the same value
            # because Django settings reads DEEPSEEK_API_KEY from the env
            # at startup.
            env_key = (
                getattr(settings, "DEEPSEEK_API_KEY", "")
                or os.environ.get("DEEPSEEK_API_KEY", "")
            )
            if env_key:
                deepseek_keys = [{"key": env_key, "status": "live", "reset_time": None}]
                api_keys_config["deepseek"] = deepseek_keys

        for key_data in deepseek_keys:
            if not key_data.get("key"):
                continue
            if key_data.get("status") != "live":
                continue
            try:
                from langchain_openai import ChatOpenAI
                llm = ChatOpenAI(
                    model=getattr(settings, "DEEPSEEK_MODEL", "deepseek-chat"),
                    api_key=key_data["key"],
                    base_url=getattr(
                        settings, "DEEPSEEK_BASE_URL", "https://api.deepseek.com",
                    ),
                    temperature=0,
                    max_tokens=int(getattr(settings, "DEEPSEEK_MAX_TOKENS", 4096)),
                    timeout=int(getattr(settings, "DEEPSEEK_TIMEOUT_SECONDS", 60)),
                )
                return llm, {
                    "provider": "deepseek",
                    "model": getattr(settings, "DEEPSEEK_MODEL", "deepseek-chat"),
                    "key": key_data["key"],
                }
            except Exception as e:
                # Most likely causes: langchain-openai not installed, or
                # bad base_url. Log and fall through to Gemini.
                print(f"[DeepSeek] init failed: {e!r} — falling through to Gemini")
                continue

    # 2. Try Gemini Fallback
    gemini_key = api_keys_config.get("gemini") or os.environ.get("GEMINI_API_KEY")
    if gemini_key and not api_keys_config.get("gemini_exhausted"):
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                google_api_key=gemini_key,
                temperature=0,
                max_retries=1,
            )
            return llm, {"provider": "gemini", "index": 0, "model": "gemini-2.5-flash", "key": gemini_key}
        except Exception as e:
            print(f"Failed to init Gemini key: {e}")

    return None, None

def _extract_json_from_text(text: str) -> str:
    """Extract a JSON object from a free-text LLM response.

    Handles these shapes:
      - raw JSON:  {"full_name": "..."}
      - fenced:    ```json\\n{...}\\n```
      - prose:     "Here is the JSON: {...}"  (first { ... last } wins)
    """
    if not text:
        return ""
    s = text.strip()
    # Strip ```json ... ``` or ``` ... ``` fences
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", s, re.DOTALL)
    if fence:
        return fence.group(1)
    # Otherwise grab the outermost {...} block
    first = s.find("{")
    last = s.rfind("}")
    if first != -1 and last != -1 and last > first:
        return s[first:last + 1]
    return s


# Map: LLM-output list field → Pydantic name field on each item.
# When the LLM returns a list of plain strings (e.g.
#   "qualifications": ["COOK CERT", "GMDSS", ...])
# instead of a list of dicts (e.g.
#   "qualifications": [{"certificate_name": "COOK CERT", ...}, ...]),
# we wrap each string in a dict with the appropriate name field and
# leave the other fields empty. The Pydantic model will accept it
# because the non-name fields all have `default=""`.
_LIST_OF_DICT_FIELDS = {
    "qualifications": "certificate_name",
    "health_certificates": "certificate_type",
    "travel_documents": "type",
}


def _coerce_list_fields_to_dicts(raw: dict) -> dict:
    """Coerce any list-of-strings fields into list-of-dicts so Pydantic
    validation passes even when the LLM emits a simpler shape."""
    if not isinstance(raw, dict):
        return raw
    for field, name_key in _LIST_OF_DICT_FIELDS.items():
        value = raw.get(field)
        if isinstance(value, list) and value and all(
            isinstance(item, str) for item in value
        ):
            raw[field] = [{name_key: item} for item in value]
    return raw


def _call_llm_with_retry(prompt: str, schema: type, api_keys_config: dict, max_retries: int = 3):
    """Call the LLM and parse the response into a Pydantic model.

    Why this doesn't use `with_structured_output`:
      Some Groq models (notably the openai/gpt-oss-120b default) wrap
      their JSON output in markdown code fences or just emit prose +
      JSON, rather than using the requested tool. LangChain's
      `with_structured_output` requires an actual tool call, so
      `openai/gpt-oss-120b` returns:
          "Tool choice is required, but model did not call a tool"
      even though the LLM extracted the right data.

    The fix below calls the LLM directly (no tool required), extracts
    the JSON from the text response, then validates with Pydantic.
    Works for every model — Ollama, Groq, Gemini.
    """
    last_exc = None
    retries = 0

    while True:
        llm, source = _get_active_llm(api_keys_config)
        if not llm:
            if last_exc:
                raise Exception("LLM providers exhausted") from last_exc
            raise Exception("LLM providers exhausted")

        try:
            # 1. Call the LLM directly (no with_structured_output)
            response = llm.invoke(prompt)
            # AIMessage has .content; ChatResult has .generations; both
            # have something we can pull a string from.
            text = getattr(response, "content", None) or str(response)

            # 2. Extract the JSON object from the text
            json_str = _extract_json_from_text(text)
            if not json_str:
                raise Exception("LLM response contained no JSON object")

            # 3. Parse JSON
            try:
                raw = json.loads(json_str)
            except json.JSONDecodeError as exc:
                raise Exception(f"LLM response is not valid JSON: {exc}") from exc

            # 4. Coerce list-of-strings to list-of-dicts (some LLMs emit
            #    simpler output where a list of objects is just a list
            #    of name strings). Without this, Pydantic validation
            #    fails on the dict-typed fields and we waste retries.
            raw = _coerce_list_fields_to_dicts(raw)

            # 5. Validate with Pydantic (now permissive — fields have defaults)
            try:
                parsed = schema(**raw)
            except Exception as exc:
                raise Exception(f"LLM JSON did not match schema: {exc}") from exc

            # 5. Token accounting + last_active (best-effort)
            try:
                usage = getattr(response, "response_metadata", {}) or {}
                usage = usage.get("token_usage", {}) or usage.get("usage", {}) or {}
                total_tokens = usage.get("total_tokens", 0)
                if total_tokens > 0:
                    provider = source.get("provider", "groq")
                    token_key = f"{provider}_tokens"
                    api_keys_config[token_key] = api_keys_config.get(token_key, 0) + total_tokens
            except Exception:
                pass

            key_val = source.get("key", "")
            masked_key = key_val[:8] + "..." if key_val else ""
            api_keys_config["last_active"] = {
                "model": source.get("model"),
                "provider": source.get("provider"),
                "key": masked_key,
            }

            return parsed
        except Exception as exc:
            err = str(exc).lower()
            last_exc = exc
            if "rate limit" in err or "429" in err or "rate_limit" in err or "quota" in err or "exhausted" in err:
                if source["provider"] == "deepseek":
                    # DeepSeek's API doesn't return a "resets in" hint
                    # we can reliably parse. Mark the key exhausted; the
                    # user can rotate it (or wait — limits are generous).
                    if api_keys_config.get("deepseek"):
                        api_keys_config["deepseek"][0]["status"] = "exhausted"
                    print("[Rate-limit] DeepSeek key exhausted. Rotate the key to recover.")
                    continue
                elif source["provider"] == "gemini":
                    api_keys_config["gemini_exhausted"] = True
                    print("[Rate-limit] Gemini key exhausted.")
                    continue
                else:
                    continue
            else:
                retries += 1
                if retries > max_retries:
                    print(f"[LLM Error] Max retries ({max_retries}) exceeded: {exc}")
                    raise exc
                else:
                    print(f"[LLM Error] Retry {retries}/{max_retries} for error: {exc}")
                    time.sleep(2)
                    continue

def _int_or_none(val: str) -> int:
    try:
        return int(re.sub(r'\D', '', val))
    except:
        return None
# =============================================================================
# COMPREHENSIVE EXTRACTION MODELS (single LLM call for all non-table sections)
# =============================================================================

class _TravelDocExtract(BaseModel):
    type: str = Field(default="", description="Passport, Seaman Book, or Other Seaman Book")
    document_no: str = Field(default="", description="Document number exactly as written")
    issue_date: str = Field(default="", description="Issue date exactly as written")
    expiry_date: str = Field(default="", description="Expiry date exactly as written")
    issued_by: str = Field(default="", description="Issuing authority name")
    place_of_issue: str = Field(default="", description="Place of issue")


class _QualExtract(BaseModel):
    certificate_name: str = Field(default="", description="Certificate name e.g. COC/Master, GOC, D.P. INDUCTION, D.P. ADVANCED, D.P. OPERATOR (UNLIMITED)")
    number: str = Field(default="", description="Certificate number")
    issue_date: str = Field(default="", description="Issue date")
    expiry_date: str = Field(default="", description="Expiry date")
    issued_by: str = Field(default="", description="Issued by authority")
    issued_at: str = Field(default="", description="Issued at location")


class _HealthCertExtract(BaseModel):
    certificate_type: str = Field(default="", description="Certificate type: International Medical, Yellow Fever, Cholera, etc.")
    number: str = Field(default="", description="Certificate number")
    issue_date: str = Field(default="", description="Issue date")
    expiry_date: str = Field(default="", description="Expiry date")
    issued_by: str = Field(default="", description="Issued by")
    issued_at: str = Field(default="", description="Issued at")


class _FullCVExtraction(BaseModel):
    """Complete seafarer CV extraction for all sections except marine courses (8) and sea service (9)."""
    # Section 0: Application Meta
    position_applied: str = Field(default="", description="Position applied for e.g. Master, Chief Officer")
    register_code: str = Field(default="", description="Register code e.g. DO-1.001")
    other_position: str = Field(default="", description="Other position if any")
    register_date: str = Field(default="", description="Registration date")
    last_update_date: str = Field(default="", description="Last update date")

    # Section 1: Personal Details
    full_name: str = Field(default="", description="APPLICANT full name from Section 1 Personal Details only")
    date_of_birth: str = Field(default="", description="Date of birth exactly as written e.g. 15/10/1983")
    nationality: str = Field(default="", description="Nationality e.g. Egyptian")
    place_of_birth: str = Field(default="", description="Place of birth")
    is_single: bool = Field(default=False, description="True ONLY if Single checkbox is visually marked/checked")
    is_married: bool = Field(default=False, description="True ONLY if Married checkbox is visually marked/checked")
    height_cm: str = Field(default="", description="Height in cm digits only")
    weight_kg: str = Field(default="", description="Weight in kg digits only")
    overall_size: str = Field(default="", description="Overall/coverall size")
    shirt_size: str = Field(default="", description="Shirt size")
    trouser_size: str = Field(default="", description="Trouser size")
    shoes_size: str = Field(default="", description="Shoes size")
    nearest_port: str = Field(default="", description="Nearest port or airport")

    # Section 2: Education
    college_school: str = Field(default="", description="College or school attended")
    marlins_issued_date: str = Field(default="", description="Marlins test issued date")
    marlins_result_pct: str = Field(default="", description="Marlins test result percentage")
    marlins_issued_by: str = Field(default="", description="Marlins test issued by authority")
    marlins_issued_at: str = Field(default="", description="Marlins test issued at location")
    english_fluent: bool = Field(default=False, description="True if English Fluent is checked")
    english_good: bool = Field(default=False, description="True if English Good is checked")
    english_average: bool = Field(default=False, description="True if English Average is checked")
    english_poor: bool = Field(default=False, description="True if English Poor is checked")
    german_fluent: bool = Field(default=False, description="True if German Fluent is checked")
    german_good: bool = Field(default=False, description="True if German Good is checked")
    german_average: bool = Field(default=False, description="True if German Average is checked")
    german_poor: bool = Field(default=False, description="True if German Poor is checked")

    # Section 3: Contact Details
    home_address: str = Field(default="", description="Full home address including city")
    email: str = Field(default="", description="Email address")
    mobile_tel: str = Field(default="", description="Mobile or telephone number")

    # Section 4: Travel Documents
    travel_documents: List[_TravelDocExtract] = Field(default_factory=list, description="All travel documents")

    # Section 5: Professional Qualifications
    qualifications: List[_QualExtract] = Field(default_factory=list, description="All professional certificates")

    # Section 6: Next of Kin / Emergency Contact
    nok_full_name: str = Field(default="", description="Emergency contact full name - NOT the applicant")
    nok_relationship: str = Field(default="", description="Relationship to applicant")
    nok_address: str = Field(default="", description="Next of kin address")
    nok_tel: str = Field(default="", description="Next of kin telephone")
    nok_mobile: str = Field(default="", description="Next of kin mobile")
    nok_email: str = Field(default="", description="Next of kin email")

    # Section 7: Health Certificates
    health_certificates: List[_HealthCertExtract] = Field(default_factory=list, description="All health certificates")
    covid_vaccine_name: str = Field(default="", description="COVID-19 vaccine name")
    covid_first_dose: str = Field(default="", description="COVID-19 first dose date")
    covid_second_dose: str = Field(default="", description="COVID-19 second dose date or remarks")

    # Section 10: References
    ref_1_company: str = Field(default="", description="Reference 1 company")
    ref_1_position: str = Field(default="", description="Reference 1 position")
    ref_1_name: str = Field(default="", description="Reference 1 name")
    ref_1_tel_email: str = Field(default="", description="Reference 1 tel/email")
    ref_2_company: str = Field(default="", description="Reference 2 company")
    ref_2_position: str = Field(default="", description="Reference 2 position")
    ref_2_name: str = Field(default="", description="Reference 2 name")
    ref_2_tel_email: str = Field(default="", description="Reference 2 tel/email")

    # Section 11: Declaration
    declaration_place: str = Field(default="", description="Declaration place")
    declaration_date: str = Field(default="", description="Declaration date")


def _format_tables_readable(tables: list) -> str:
    """Format extracted tables in a clean readable format for the LLM."""
    if not tables:
        return "(no tables extracted)"
    parts = []
    for i, table in enumerate(tables):
        if not table:
            continue
        lines = []
        for row in table:
            cells = []
            for cell in row:
                cells.append(cell.strip() if cell and cell.strip() else "(empty)")
            lines.append(" | ".join(cells))
        parts.append(f"--- TABLE {i+1} ---\n" + "\n".join(lines))
    return "\n\n".join(parts) if parts else "(no tables extracted)"


def _build_comprehensive_prompt(text: str, tables: list) -> str:
    """Build a single comprehensive LLM prompt for extracting all CV sections (except marine courses and sea service)."""
    tables_text = _format_tables_readable(tables)

    return f"""You are an expert maritime CV data extractor. Extract ALL data from this seafarer employment application.

## ABSOLUTE RULES:
1. Copy every value EXACTLY as it appears. Do NOT rephrase, translate, or modify anything.
2. If a field is empty or not found -> return empty string "".
3. DO NOT hallucinate or invent data. Only extract what is explicitly written.
4. "full_name" = the APPLICANT's name from "1. PERSONAL DETAILS" section ONLY.
5. "nok_full_name" = the EMERGENCY CONTACT name from "6. NEXT OF KIN" section. This is a DIFFERENT person.
6. For Marital Status checkboxes: In the original document, one box is marked. Look for the checkbox symbol next to Single or Married. Set is_single=true or is_married=true accordingly.
7. For English/German language: set ONLY the level that has a checkmark. All others must be false.
8. Dates: copy exactly as written. e.g. "15/10/1983", "26/07/2020", "01/18", "16/05/2022".
9. For Travel Documents: extract Passport, Seaman Book, and Other Seaman Book as separate entries.
10. For Qualifications: extract ALL certificates including COC/Master, GOC, D.P. INDUCTION, D.P. ADVANCED, D.P. OPERATOR (UNLIMITED), etc.
11. For Health Certificates: extract ALL listed (International Medical, Yellow Fever, Cholera, etc.)

## FULL DOCUMENT TEXT:
{text}

## STRUCTURED TABLE DATA FROM DOCUMENT:
{tables_text}

Extract ALL data following the schema. Empty/missing fields must be empty strings ""."""


def _map_comprehensive_result(r: '_FullCVExtraction', base: dict) -> dict:
    """Map the comprehensive LLM extraction back to the numbered section format."""

    def p(llm_val, fallback=""):
        """Prefer LLM value if non-empty."""
        if llm_val and str(llm_val).strip():
            return str(llm_val).strip()
        return fallback

    b = base  # shorthand

    # Section 0
    b["0_application_meta"] = {
        "application_for_position_as": p(r.position_applied, b.get("0_application_meta", {}).get("application_for_position_as", "")),
        "register_code": p(r.register_code, b.get("0_application_meta", {}).get("register_code", "")),
        "other_position": p(r.other_position, b.get("0_application_meta", {}).get("other_position", "")),
        "register_date": p(r.register_date, b.get("0_application_meta", {}).get("register_date", "")),
        "last_update_data": p(r.last_update_date, b.get("0_application_meta", {}).get("last_update_data", "")),
    }

    # Section 1
    b["1_personal_details"] = {
        "full_name": p(r.full_name, b.get("1_personal_details", {}).get("full_name", "")),
        "date_of_birth": p(r.date_of_birth, b.get("1_personal_details", {}).get("date_of_birth", "")),
        "marital_status": {"single": r.is_single, "married": r.is_married},
        "nationality": p(r.nationality, b.get("1_personal_details", {}).get("nationality", "")),
        "height_cm": _int_or_none(r.height_cm) if r.height_cm else b.get("1_personal_details", {}).get("height_cm"),
        "weight_kg": _int_or_none(r.weight_kg) if r.weight_kg else b.get("1_personal_details", {}).get("weight_kg"),
        "place_of_birth": p(r.place_of_birth, b.get("1_personal_details", {}).get("place_of_birth", "")),
        "overall_size": p(r.overall_size, b.get("1_personal_details", {}).get("overall_size", "")),
        "shirt_size": p(r.shirt_size, b.get("1_personal_details", {}).get("shirt_size", "")),
        "nearest_port": p(r.nearest_port, b.get("1_personal_details", {}).get("nearest_port", "")),
        "trouser_size": p(r.trouser_size, b.get("1_personal_details", {}).get("trouser_size", "")),
        "shoes_size": p(r.shoes_size, b.get("1_personal_details", {}).get("shoes_size", "")),
    }

    # Section 2
    b["2_education"] = {
        "college_school": p(r.college_school, b.get("2_education", {}).get("college_school", "")),
        "marline_test": {
            "issued_date": p(r.marlins_issued_date),
            "result_percentage": p(r.marlins_result_pct),
            "issued_by_authority": p(r.marlins_issued_by),
            "issued_at": p(r.marlins_issued_at),
        },
        "english_language": {
            "fluent": r.english_fluent,
            "good": r.english_good,
            "average": r.english_average,
            "poor": r.english_poor,
        },
        "german_language": {
            "fluent": r.german_fluent,
            "good": r.german_good,
            "average": r.german_average,
            "poor": r.german_poor,
        },
    }

    # Section 3
    b["3_contact_details"] = {
        "home_address_city": p(r.home_address, b.get("3_contact_details", {}).get("home_address_city", "")),
        "e_mail": p(r.email, b.get("3_contact_details", {}).get("e_mail", "")),
        "mobile_tel": p(r.mobile_tel, b.get("3_contact_details", {}).get("mobile_tel", "")),
    }

    # Section 4
    if r.travel_documents:
        b["4_travel_documents"] = [
            {
                "type": p(td.type),
                "document_no": p(td.document_no),
                "iss_date": p(td.issue_date),
                "exp_date": p(td.expiry_date),
                "iss_by_authority": p(td.issued_by),
                "place_of_issue": p(td.place_of_issue),
            }
            for td in r.travel_documents
        ]

    # Section 5
    if r.qualifications:
        b["5_professional_qualification_certificate_of_competency"] = [
            {
                "certificate_name": p(q.certificate_name),
                "number": p(q.number),
                "issue_date": p(q.issue_date),
                "expiry_date": p(q.expiry_date),
                "issued_by": p(q.issued_by),
                "issued_at": p(q.issued_at),
            }
            for q in r.qualifications
        ]

    # Section 6
    nok = b.get("6_next_of_kin_emergency_contact", {})
    b["6_next_of_kin_emergency_contact"] = {
        "full_name": p(r.nok_full_name, nok.get("full_name", "")),
        "relationship": p(r.nok_relationship, nok.get("relationship", "")),
        "address_country": p(r.nok_address, nok.get("address_country", "")),
        "tel_no_mobile": p(r.nok_tel or r.nok_mobile, nok.get("tel_no_mobile", "")),
        "email": p(r.nok_email, nok.get("email", "")),
        "address": p(r.nok_address, nok.get("address", "")),
        "tel_no": p(r.nok_tel, nok.get("tel_no", "")),
        "mobile": p(r.nok_mobile, nok.get("mobile", "")),
    }

    # Section 7
    if r.health_certificates:
        certs = []
        for hc in r.health_certificates:
            certs.append({
                "flag_state": p(hc.certificate_type),
                "number": p(hc.number),
                "issue_date": p(hc.issue_date),
                "expiry_date": p(hc.expiry_date),
                "issued_by": p(hc.issued_by),
                "issued_at": p(hc.issued_at),
            })
        b["7_health_certificates_and_vaccinations"] = {
            "certificates": certs,
            "covid_19": {
                "vaccination_name": p(r.covid_vaccine_name),
                "first_dose": p(r.covid_first_dose),
                "second_dose": p(r.covid_second_dose),
            },
        }

    # Section 10
    refs = []
    if r.ref_1_company or r.ref_1_name:
        refs.append({
            "no": "1",
            "company_management_country": p(r.ref_1_company),
            "position": p(r.ref_1_position),
            "name": p(r.ref_1_name),
            "tel_email": p(r.ref_1_tel_email),
        })
    if r.ref_2_company or r.ref_2_name:
        refs.append({
            "no": "2",
            "company_management_country": p(r.ref_2_company),
            "position": p(r.ref_2_position),
            "name": p(r.ref_2_name),
            "tel_email": p(r.ref_2_tel_email),
        })
    if refs:
        b["10_references"] = refs

    # Section 11
    b["11_declaration"] = {
        "health_questions": b.get("11_declaration", {}).get("health_questions", {}),
        "consent_statement": b.get("11_declaration", {}).get("consent_statement", ""),
        "place": p(r.declaration_place, b.get("11_declaration", {}).get("place", "")),
        "date": p(r.declaration_date, b.get("11_declaration", {}).get("date", "")),
        "signature": b.get("11_declaration", {}).get("signature", ""),
    }

    return b


# --- MARINE COURSES AND SEA SERVICE MODELS ---
class _MarineCourse(BaseModel):
    course_name: str = Field(...)
    number: str = Field(...)
    issue_date: str = Field(...)
    expiry_date: str = Field(...)
    issued_by_at: str = Field(...)

class _SpecialisedExperience(BaseModel):
    name: str = Field(...)
    type: str = Field(...)
    from_date: str = Field(...)
    to_date: str = Field(...)
    comments: str = Field(...)

class _SeaServiceRecord(BaseModel):
    company_name: str = Field(...)
    rank: str = Field(...)
    vessel_name: str = Field(...)
    imo_number: str = Field(...)
    flag: str = Field(...)
    signed_on: str = Field(...)
    signed_off: str = Field(...)
    period: str = Field(...)
    vessel_type: str = Field(...)
    dwt: str = Field(...)
    grt: str = Field(...)
    engine_type: str = Field(...)
    bh: str = Field(...)
    kw: str = Field(...)
    reason_for_sign_off: str = Field(...)

class _StageTwoResult(BaseModel):
    courses: List[_MarineCourse] = Field(default_factory=list)
    service_records: List[_SeaServiceRecord] = Field(default_factory=list)
    specialised_experience: List[_SpecialisedExperience] = Field(default_factory=list)

def _build_stage_two_prompt(text: str, table_text: str, applicant_name: str) -> str:
    return f"""You are an expert maritime CV data extractor. Extract Marine Courses and Sea Service records from this seafarer CV.

## ABSOLUTE RULES:
1. Copy every value EXACTLY as it appears. Do NOT rephrase, translate, or modify anything.
2. If a field is empty or not found -> return empty string "".
3. DO NOT hallucinate or invent data. Only extract what is explicitly written.
4. Dates: copy exactly as written. e.g. "15/10/1983", "26/07/2020", "16/05/2022".
5. For Sea Service: extract EVERY row from the sea service table — even if it has the same vessel/rank repeated.
6. Output ONLY valid JSON, no markdown fences, no explanation, no preamble.

## APPLICANT: {applicant_name}

## FULL DOCUMENT TEXT:
{text}

## STRUCTURED TABLE DATA FROM DOCUMENT:
{table_text}

Return a JSON object with three fields:
  - "courses": array of marine course objects {{course_name, number, issue_date, expiry_date, issued_by_at}}
  - "service_records": array of sea service objects {{company_name, rank, vessel_name, imo_number, flag, from_date, to_date, vessel_type, dwt, grt, engine_type, bh, kw, reason_for_sign_off}}
  - "specialised_experience": array of objects {{name, type, from_date, to_date, comments}}

Empty arrays are fine. Empty strings for missing values."""
# =============================================================================
# MAIN FUNCTION — comprehensive LLM extraction with Groq
# =============================================================================

def convert_text_to_json(
    extracted_text: str,
    parsed_tables: list = None,
    api_keys_config: dict = None,
) -> dict:
    """
    Convert extracted CV text into a structured numbered dict.
    Uses multi-stage LLM extraction with api_keys_config router.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    tables = parsed_tables or []
    text   = extracted_text or ""

    # -- 1. Maritime CV validation ---------------------------------------------
    maritime_keywords = [
        'passport', 'seaman', 'coc', 'goc', 'rank', 'vessel', 'ship',
        'marine', 'maritime', 'stcw', 'certificate', 'sea service',
        'nationality', 'date of birth', 'personal details', 'marital status',
        'next of kin', 'emergency contact', 'vaccination', 'health certificate',
        'fire fighting', 'survival', 'sailor', 'officer', 'engineer',
        'captain', 'chief', 'deck', 'engine', 'flag state', 'imo',
        'dwt', 'grt', 'signed on', 'signed off', 'full name', 'port',
    ]
    text_lower = text.lower()
    keyword_count = sum(1 for kw in maritime_keywords if kw in text_lower)
    print(f"[CV Validation] {keyword_count} maritime keywords found | text length: {len(text.strip())} chars")

    if keyword_count < 3 or len(text.strip()) < 100:
        print("[CV Validation] REJECTED - not a valid maritime CV")
        return {"validation_error": "Document is not a valid maritime CV or contains too little text"}, api_keys_config

    local_result = {}

    # -- 2. Pick an LLM provider (Ollama local, DeepSeek, or Gemini) -----------
    # An empty api_keys_config is fine when Ollama is running — the
    # router in _get_active_llm will pick it up. We only return a
    # hard error when there's NO LLM reachable at all.
    has_cloud_keys = bool(api_keys_config.get("deepseek")) or bool(
        api_keys_config.get("gemini")
    ) or bool(os.environ.get("DEEPSEEK_API_KEY")) or bool(
        os.environ.get("GEMINI_API_KEY")
    )
    ollama_configured = bool(getattr(settings, "OLLAMA_HOST", ""))

    if not has_cloud_keys and not ollama_configured:
        print("[LLM] CRITICAL ERROR: No LLM provider available.")
        return {
            "validation_error": (
                "No LLM provider is available. Either:\n"
                "  - Set OLLAMA_HOST env var (e.g. http://127.0.0.1:11434) "
                "and run `ollama pull qwen2.5:7b` for a free local LLM, OR\n"
                "  - Set DEEPSEEK_API_KEY env var, OR\n"
                "  - Supply a DeepSeek key in the request (`deepseek_api_key` "
                "form field) for the cloud LLM fallback."
            )
        }, api_keys_config

    try:
        # -- Pass 1: COMPREHENSIVE (sections 0-7, 10-12) -----------------------
        print("[Stage 2 / Pass 1] Comprehensive LLM extraction - all non-table sections...")
        try:
            comp_prompt = _build_comprehensive_prompt(text, tables)
            comp_result = _call_llm_with_retry(comp_prompt, _FullCVExtraction, api_keys_config)
            if comp_result:
                local_result = _map_comprehensive_result(comp_result, local_result)
                print("[Stage 2 / Pass 1] Comprehensive extraction successful.")
            else:
                print("[Stage 2 / Pass 1] LLM returned empty.")
        except Exception as exc:
            import traceback
            traceback.print_exc()
            logger.warning(f"Comprehensive LLM pass failed: {exc}")
            raise exc  # Pass 1 is critical — cannot continue without it

        time.sleep(1)

        # -- Pass 2: Marine Courses and Sea Service (Sections 8 & 9) -----------
        # Skip Pass 2's LLM call by default. Pass 2 doubles the request
        # time (60+s total) which Cloudflare's free/proxy tier 504s.
        # Trade-off: marine courses + sea service come back empty for
        # non-Sakr CVs. Set DEEPSEEK_RUN_PASS2=true in the env (or in
        # the systemd unit) to re-enable. (We'll add pdfplumber-table-
        # based extraction as a faster, free replacement later.)
        if not getattr(settings, "DEEPSEEK_RUN_PASS2", False):
            print("[Stage 2 / Pass 2] Skipped (DEEPSEEK_RUN_PASS2=false). "
                  "Set env var to true to re-enable.")
        else:
            table_text = _format_tables_readable(tables)
            applicant_name = (local_result.get("1_personal_details") or {}).get("full_name", "")

            print("[Stage 2 / Pass 2] LLM extraction - Marine Courses and Sea Service...")
            try:
                stage_two_prompt = _build_stage_two_prompt(text, table_text, applicant_name=applicant_name)
                # max_retries=1 (not 3) so a Pass-2 hiccup doesn't make the
                # whole request hang for 60+ seconds on the gunicorn boundary.
                # Pass 2 is non-critical — Pass 1 already saved the bulk of
                # the CV.
                stage_two_result = _call_llm_with_retry(stage_two_prompt, _StageTwoResult, api_keys_config, max_retries=1)

                if stage_two_result:
                    # Map Marine Courses
                    if stage_two_result.courses:
                        local_result["8_marine_courses"] = [
                            {
                                "course_name":  c.course_name,
                                "number":       c.number,
                                "issue_date":   c.issue_date,
                                "expiry_date":  c.expiry_date,
                                "issued_by_at": c.issued_by_at,
                            }
                            for c in stage_two_result.courses
                        ]
                        print(f"[Stage 2 / Pass 2] Extracted {len(stage_two_result.courses)} marine courses.")

                    # Map Sea Service
                    if stage_two_result.service_records:
                        existing_info = (local_result.get("9_complete_sea_service_details") or {}).get(
                            "applicant_info", {}
                        )
                        local_result["9_complete_sea_service_details"] = {
                            "applicant_info": existing_info,
                            "service_records": [
                                {
                                    "company_name":          r.company_name,
                                    "rank":                  r.rank,
                                    "vessel_name":           r.vessel_name,
                                    "imo_number":            r.imo_number,
                                    "flag":                  r.flag,
                                    "signed_on":             r.signed_on,
                                    "signed_off":            r.signed_off,
                                    "period":                r.period,
                                    "vessel_type":           r.vessel_type,
                                    "dwt":                   r.dwt,
                                    "grt":                   r.grt,
                                    "engine_type":           r.engine_type,
                                    "bh":                    r.bh,
                                    "kw":                    r.kw,
                                    "reason_for_sign_off":   r.reason_for_sign_off,
                                }
                                for r in stage_two_result.service_records
                            ],
                            "specialised_experience": [
                                {
                                    "name":                  s.name,
                                    "type":                  s.type,
                                    "from_date":             s.from_date,
                                    "to_date":               s.to_date,
                                    "comments":              s.comments,
                                }
                                for s in getattr(stage_two_result, "specialised_experience", [])
                            ],
                        }
                        print(f"[Stage 2 / Pass 2] Extracted {len(stage_two_result.service_records)} sea service records.")

            except Exception as exc:
                if "exhausted" in str(exc).lower():
                    logger.warning(f"Pass 2 failed (keys exhausted): {exc}")
                    raise exc
                else:
                    logger.warning(f"Pass 2 LLM failed (non-fatal): {exc}")

    except Exception as e:
        if "exhausted" in str(e).lower():
            return {"validation_error": "API Keys exhausted"}, api_keys_config
        return {"validation_error": str(e)}, api_keys_config

    if not local_result or len(local_result) == 0:
        return {"validation_error": "Extraction yielded no data. Please ensure the API keys are correct and valid."}, api_keys_config

    print("[Done] Extraction complete.")
    return local_result, api_keys_config
