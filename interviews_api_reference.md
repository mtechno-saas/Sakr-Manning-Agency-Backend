# 🗓️ Interviews — API Reference

The Interviews section manages the scheduling, coordination, and feedback for seafarer evaluations with client companies.

---

## 1. Description
This section provides a centralized calendar-like management for all recruitment interviews. It allows HR and Recruiters to schedule sessions, assign interviewers, provide meeting links, and record final results and technical feedback.

**Key Features:**
- **Scheduling:** Manage dates, times, and durations for various interview types.
- **Coordination:** Store meeting links (Zoom/Teams) and interviewer contact details.
- **Feedback Loop:** Record detailed notes and feedback to inform the final hiring decision.
- **Outcome Tracking:** Track results from `Pending` to `Passed`, `Failed`, or `On Hold`.

---

## 2. Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/interviews/` | List all scheduled/past interviews |
| `POST` | `/api/interviews/` | Schedule a new interview |
| `GET` | `/api/interviews/{id}/` | Retrieve full interview details |
| `PATCH` | `/api/interviews/{id}/` | Update status, result, or feedback |
| `DELETE` | `/api/interviews/{id}/` | Remove/Cancel an interview record |
| `GET` | `/api/interviews/stats/` | KPIs (Upcoming today, pass rate, etc.) |

---

## 3. Endpoint Details

### 3.1 Schedule Interview (`POST /api/interviews/`)
**Description:** Schedules a new session for a candidate.
- **Request Body:**
| Field | Type | Description |
|---|---|---|
| `candidate` | Integer | ID of the Seafarer (Required) |
| `company` | Integer | ID of the target Company (Required) |
| `position` | Mixed | Rank ID or Name (e.g. "Master") |
| `scheduled_date`| Date | Format: `YYYY-MM-DD` |
| `scheduled_time`| Time | Format: `HH:MM` |
| `interview_type`| String | `Phone`, `Video`, `In-Person`, `Technical` |
| `meeting_link` | URL | Link to Zoom/Teams session |

**Example Request:**
```json
{
  "candidate": 105,
  "company": 3,
  "position": "Chief Officer",
  "scheduled_date": "2026-05-20",
  "scheduled_time": "14:00",
  "interview_type": "Video",
  "meeting_link": "https://zoom.us/j/123456789"
}
```

### 3.2 Update Result (`PATCH /api/interviews/{id}/`)
**Description:** Records the outcome and interviewer feedback.
- **Example Request:**
```json
{
  "status": "Completed",
  "result": "Passed",
  "feedback": "Strong technical knowledge, excellent English level. Recommended for hire.",
  "notes": "Candidate was 5 minutes late but performed well."
}
```

---

## 4. Data Modeling

### Interview Model
| Field | Type | Description |
|---|---|---|
| `id` | Integer | Unique identifier |
| `candidate` | FK | Link to the Seafarer |
| `company` | FK | Link to the Client Company |
| `position` | FK | Target Rank |
| `scheduled_date` | Date | Date of the interview |
| `scheduled_time` | Time | Time of the interview |
| `status` | Choice | `Scheduled`, `Completed`, `Cancelled`, `No Show` |
| `result` | Choice | `Pending`, `Passed`, `Failed`, `On Hold` |
| `meeting_link` | URL | Remote interview link |
| `feedback` | Text | Technical/Soft skill evaluation |

---

## 5. Permissions

- **Admin / HR Manager / Recruiter:** Full access to schedule and review all interviews.
- **Employee (Seafarer):** Can only view their own scheduled interviews (read-only). Cannot see internal feedback or notes until explicitly shared.

---

> [!TIP]
> The `stats/` endpoint returns a count of interviews scheduled for "Today," which is useful for building a daily agenda widget on the dashboard.
