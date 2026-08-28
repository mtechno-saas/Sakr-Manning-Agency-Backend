# AI CV Upload API

`POST /ai/upload/` — the LLM-backed CV parsing endpoint. This is the
end-user-facing version (admin authentication required). The response
shape matches `POST /ai/parse/` (deterministic dry-run probe) but
adds persistence: a `Users` row + a `CVSubmission` row are created
when the email is new or attached to the existing user.

Related docs:
- `/ai/parse/` — the same parser without save (deterministic dry-run)
- `/api/cv-submissions/` — list/manage saved CVs
- `docs/ollama-local-llm-setup.md` — how Ollama is wired up

---

## Endpoint

| | |
|---|---|
| **Method** | `POST` |
| **URL** | `/ai/upload/` |
| **Auth** | Bearer JWT (admin or any authenticated user with `CVPermission`) |
| **Content-Type** | `multipart/form-data` |
| **Backend** | `ai_document.views.DocumentUploadView` |
| **Code** | `ai_document/views.py:3554` |

---

## Request (multipart form)

| Field | Type | Required | Notes |
|---|---|---|---|
| `file` | File (PDF or DOCX) | yes | Sakr-form template or free-form |
| `save_to_db` | string | no | `"true"` (default) or `"false"`. `"false"` = dry-run parse, no DB writes |
| `groq_api_key` | string | no | Per-request Groq key. Not needed when Ollama is up. |
| `api_keys_config` | string (JSON) | no | Full key config for LLM providers |

### Sample curl

```bash
# Save to DB (default)
curl -X POST http://127.0.0.1:8000/ai/upload/ \
  -H "Authorization: Bearer $ADMIN_JWT" \
  -F "file=@/path/to/seafarer_cv.pdf"

# Dry-run (parse only, no DB writes)
curl -X POST http://127.0.0.1:8000/ai/upload/ \
  -H "Authorization: Bearer $ADMIN_JWT" \
  -F "file=@/path/to/seafarer_cv.pdf" \
  -F "save_to_db=false"
```

---

## Response — Success (HTTP 200)

```json
{
  "success": true,
  "extractor": "sakr_template" | "groq_llm",
  "confidence": 0.95,
  "data": {
    "0_application_meta": {
      "application_for_position_as": "Bar Attendant Lounge",
      "register_code": "DR-6.104",
      "other_position": "Waiter Restaurant",
      "register_date": "10.07.2025",
      "expected_salary": "730 $",
      "available_date": "25/7/2025"
    },
    "1_personal_details": {
      "full_name": "MOHAMED SHEHATA RAMADAN ABDEL BASSET",
      "date_of_birth": "28/02/1995",
      "nationality": "Egyptian",
      "height_cm": 173,
      "weight_kg": 67,
      "place_of_birth": "Qena, Egypt",
      "marital_status": { "single": true, "married": false }
    },
    "2_education": { ... },
    "3_contact_details": {
      "home_address_city": "Qena - Qena - Sheikh Younis",
      "e_mail": "MOHASHEHATA1995@GMAIL.COM",
      "mobile_tel": "00201090946284"
    },
    "4_travel_documents": [ ... ],
    "5_professional_qualification_certificate_of_competency": [ ... ],
    "6_next_of_kin_emergency_contact": { ... },
    "7_health_certificates_and_vaccinations": { ... },
    "8_marine_courses": [ ... ],
    "9_complete_sea_service_details": { ... },
    "10_references": [ ... ],
    "11_declaration": { ... },
    "12_for_office_use_only": { ... }
  },
  "warnings": [],
  "file_name": "seafarer_cv.pdf",
  "ocr": {
    "ocr_applied": false,
    "ocr_pages_processed": 0,
    "ocr_backend": null
  },
  "saved": true,
  "user_id": 123,
  "cv_submission_id": 456
}
```

### Top-level fields

| Field | Type | Notes |
|---|---|---|
| `success` | bool | Always `true` on HTTP 200 |
| `extractor` | string | `"sakr_template"` (deterministic, 0.95 confidence) or `"groq_llm"` (LLM-based, 0.7 confidence) |
| `confidence` | float | 0.95 (deterministic) or 0.7 (LLM) |
| `data` | object | The 12-section numbered CV structure. See below. |
| `warnings` | array | Validation warnings (mostly empty for clean CVs) |
| `file_name` | string | The uploaded file's name (echoed back) |
| `ocr` | object | OCR meta — see below |
| `saved` | bool | `true` if `save_to_db=true` (default) and the save succeeded |
| `user_id` | int | New or existing `Users.id` (only when `saved=true`) |
| `cv_submission_id` | int | New `CVSubmission.id` (only when `saved=true`) |

### `data` — the 12-section numbered format

The LLM/deterministic parser always returns these 12 sections, even if empty:

| Key | Section |
|---|---|
| `0_application_meta` | Position applied, register code, expected salary, available date |
| `1_personal_details` | Full name, DOB, nationality, marital status, height/weight, place of birth, nearest port |
| `2_education` | College/school, Marlin's test, English/German proficiency |
| `3_contact_details` | Home address, email, phone |
| `4_travel_documents` | Array of {type, document_no, iss_date, exp_date, iss_by_authority, place_of_issue} |
| `5_professional_qualification_certificate_of_competency` | Array of cert objects |
| `6_next_of_kin_emergency_contact` | NOK full name, relationship, address, phone, email |
| `7_health_certificates_and_vaccinations` | Health certs + COVID vaccine info |
| `8_marine_courses` | Array of marine course objects |
| `9_complete_sea_service_details` | Sea service records + specialised experience |
| `10_references` | Array of reference objects |
| `11_declaration` | Declaration place + date |
| `12_for_office_use_only` | Internal office use fields |

> **Important for frontend**: the LLM produces *simplified* field names
> internally (`email`, `mobile`) but the `data` dict is normalized to the
> field names shown above (`e_mail`, `mobile_tel`) by
> `_map_comprehensive_result()`. Always use the canonical names.

### `ocr` — OCR meta (when `ocr_applied=true`)

| Field | Type | Notes |
|---|---|---|
| `ocr_applied` | bool | `true` if the document was image-based and OCR was triggered |
| `ocr_pages_processed` | int | Number of pages OCR'd (capped at `OCR_MAX_PAGES=10` by default) |
| `ocr_backend` | string | `"ollama"` (local) or `"gemini"` (cloud fallback) |

---

## Response — Errors

All errors return `success: false` and a typed `error` code. The HTTP
status code matches the error category (400 for client errors, 500
for server errors).

| HTTP | `error` | When |
|---|---|---|
| 400 | `file_missing` | No file in the request |
| 400 | `file_unsupported_format` | File isn't a PDF or DOCX |
| 400 | `not_sakr_template` | Deterministic parser doesn't recognise the Sakr form (and no LLM ran) |
| 400 | `invalid_document` | LLM ran but the text isn't a maritime CV (or OCR text too sparse) |
| 400 | `llm_empty` | LLM returned no data |
| 400 | `api_keys_missing` | No LLM provider reachable and no key supplied |
| 400 | `email_missing` | CV has no email — can't create User row |
| 500 | `llm_failed` | LLM call raised an exception |
| 500 | `llm_bad_response` | LLM returned non-dict response |
| 500 | `internal_error` | Unexpected exception (see server logs) |

### Sample error response

```json
{
  "success": false,
  "error": "invalid_document",
  "message": "Document is not a valid maritime CV or contains too little text",
  "file_name": "seafarer_cv.pdf",
  "warnings": []
}
```

---

## Extraction pipeline (routing)

The view runs the upload through this pipeline:

```
PDF/DOCX
  → DocumentProcessor.process_document(file)
      → text extraction (PyMuPDF / pdfplumber / python-docx)
      → if extracted_text < OCR_MIN_WORDS (30):
           → OCR fallback (Ollama local → Gemini cloud)
                ocr.ocr_applied = true
                ocr.ocr_pages_processed = N
                ocr.ocr_backend = "ollama"
  → SakrTemplateExtractor(text, tables)
      → if matched (Sakr form):
           → return deterministic result (extractor="sakr_template", 0.95)
      → else fall through to LLM
  → LLM (Ollama → Groq → Gemini, in priority order)
      → return LLM result (extractor="groq_llm", 0.7)
  → save_to_db (default true):
      → _save_parser_output(data, file)
           → creates/updates Users + creates CVSubmission
           → sends OTP email to seafarer
           → returns (user_id, cv_submission_id)
```

### When the deterministic parser wins

If the CV matches the Sakr form template (labelled sections, checkbox
fields, etc.), the deterministic parser handles it in <1 second with
**0.95 confidence**, no LLM call, no API cost.

### When the LLM kicks in

Free-form CVs (not Sakr-form) get routed to the LLM. Provider
priority:
1. **Ollama** (local, free, private) — when `OLLAMA_HOST` env var is set
2. **Groq** (cloud) — when a Groq key is in env or per-request
3. **Gemini** (cloud) — last resort

LLM extraction typically takes **5-15 seconds** and returns
`extractor: "groq_llm"` with 0.7 confidence. The `groq_llm` label is
generic — the actual provider is whatever answered the request.

### When OCR kicks in

Image-based PDFs (scans) have no extractable text. If the regular
text extraction returns <30 words, OCR runs first. Configure with:
- `OCR_BACKEND=ollama` (default) or `gemini`
- `OCR_MODEL=glm-ocr:latest` (default), `llava:7b`, `qwen2-vl:7b`
- `OCR_MAX_PAGES=10` (cap to avoid runaway processing)

Note: `glm-ocr:latest` is currently known to have a runaway-generation
issue. Use `llava:7b` for production OCR.

---

## Frontend integration notes

### UI flow

1. User picks a file → show loading spinner
2. POST to `/ai/upload/` with the file
3. On 200 success: show extracted data (from `data` object) for review, then
   confirm to save (or auto-save if `save_to_db=true` was sent)
4. On 400 with `error: invalid_document`: show "We couldn't read this CV.
   Try a clearer scan or a text-based file."
5. On 400 with `error: email_missing`: show "This CV has no email
   address. Please add one and re-upload."
6. On 500: show "Something went wrong. Please try again or contact support."

### Field mapping for the user display

The `data` dict uses Sakr-form field names. For the user-facing
display, you probably want to map a few key fields:
- `data["1_personal_details"]["full_name"]` → "Full name" field
- `data["3_contact_details"]["e_mail"]` → "Email" field
- `data["3_contact_details"]["mobile_tel"]` → "Phone" field
- `data["0_application_meta"]["application_for_position_as"]` → "Position" field

### `saved`, `user_id`, `cv_submission_id`

If `saved: true`:
- The `Users` row was created (or the existing one was updated) with the
  extracted data
- A `CVSubmission` row was created with the uploaded file
- The seafarer received a welcome email at their email address

If `saved: false` (you sent `save_to_db=false`):
- No DB writes happened
- The `data` is still returned for review
- Use `user_id` and `cv_submission_id` for follow-up actions (only present when `saved: true`)

### Polling vs waiting

LLM extraction can take 5-15 seconds. The endpoint is synchronous —
just show a spinner and wait for the response. Don't poll. If you
need to show progress, watch for the `extractor` field in the
response: `"sakr_template"` is fast (<1s), `"groq_llm"` is slow (5-15s).

---

## Testing locally

The repo has 4 real CV fixtures you can use for testing:

- `ai_document/tests/fixtures/cvs/01_image_based_single_page_anas_mostafa.pdf` (image-based, needs OCR)
- `ai_document/tests/fixtures/cvs/02_text_sakr_like_mohamed_fathi.pdf` (Sakr form, deterministic)
- `ai_document/tests/fixtures/cvs/03_text_non_sakr_motorman.pdf` (free-form, LLM)
- `ai_document/tests/fixtures/cvs/04_image_based_24pages_oiler.pdf` (image-based, needs OCR)

```bash
# Get an admin token
TOKEN=$(cd /opt/sakr/Sakr-Manning-Agency-Backend-New && source venv/bin/activate && \
  python manage.py shell -c "
from rest_framework_simplejwt.tokens import RefreshToken
from api.models import Users
u = Users.objects.get(email='admin@sakrshipping.com')
print(RefreshToken.for_user(u).access_token)
" 2>/dev/null | tail -1)

# Test all 4
for f in /opt/sakr/Sakr-Manning-Agency-Backend-New/ai_document/tests/fixtures/cvs/*.pdf; do
  echo "=== $(basename $f) ==="
  curl -X POST http://127.0.0.1:8000/ai/upload/ \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$f" \
    -w "\nHTTP %{http_code}\n"
done
```
