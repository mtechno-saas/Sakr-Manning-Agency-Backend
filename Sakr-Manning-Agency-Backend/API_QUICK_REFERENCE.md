# 🚢 Manning Agency API - Quick Reference

## 🎯 Project Overview

**Type**: Django REST Framework API  
**Purpose**: Maritime Manning Agency Management System  
**Authentication**: JWT (JSON Web Tokens)  
**Database**: SQLite (dev) / PostgreSQL (production-ready)

---

## 📱 What This API Does

This is a complete backend system for managing maritime manning agencies. It handles:

1. **👥 Seafarer Management** - Complete profiles with 100+ fields
2. **📋 Employment Contracts** - Track assignments to ships
3. **🚢 Fleet Management** - Ships and company information
4. **📄 Document Management** - Tickets, papers, certificates
5. **💰 Finance Tracking** - Automated payment calculations
6. **🤖 AI Processing** - Automated CV/document extraction

---

## 🗂️ Project Structure

```
django-test/
├── api/              # 👥 Users, Contracts, Certificates, Ranks
├── ships/            # 🚢 Ship management
├── companies/        # 🏢 Company management
├── tickets_papers/   # 📄 Document uploads
├── core/             # 🌍 Reference data (Flags, Vessel Types)
├── finance/          # 💰 Financial records
├── ai_agents/        # 🤖 AI chat & search
├── ai_document/      # 📝 AI document processing
└── saker/            # ⚙️ Main project settings
```

---

## 🔑 Quick Start

### 1. Get Access Token

```bash
# Register
POST /api/register/
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "first_name": "John"
}

# Login
POST /api/login/
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}

# Returns:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 2. Use Token in Requests

```bash
Authorization: Bearer <access_token>
```

---

## 📊 API Endpoints Summary

### 🔐 Authentication (Public)

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/register/` | Register new user |
| POST | `/api/login/` | Get JWT tokens |
| POST | `/api/login/refresh/` | Refresh access token |

### 👥 Users & Profiles

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/users/` | List all users |
| POST | `/api/users/` | Create user |
| GET | `/api/users/<id>/` | Get user details |
| PUT/PATCH | `/api/users/<id>/` | Update user |
| DELETE | `/api/users/<id>/` | Delete user |
| GET | `/api/filter/` | Filter users by criteria |

### 📜 Certificates & Ranks

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/certificates/` | List all certificates (102 types) |
| GET | `/api/ranks/` | List all ranks (51 types) |
| GET | `/api/users/<id>/certificates/` | Get user's certificates |
| POST | `/api/users/<id>/certificates/add/` | Add certificate to user |
| GET | `/api/users/<id>/ranks/` | Get user's ranks |
| POST | `/api/users/<id>/ranks/add/` | Add rank to user |

### 📋 Contracts

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/contracts/` | List all contracts |
| POST | `/api/contracts/` | Create contract |
| GET | `/api/contracts/<id>/` | Get contract details |
| PUT/PATCH | `/api/contracts/<id>/` | Update contract |
| DELETE | `/api/contracts/<id>/` | Delete contract |

### 🚢 Ships

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/ships/` | List all ships |
| POST | `/api/ships/` | Create ship |
| GET/PUT/DELETE | `/api/ships/<id>/` | Manage ship |

### 🏢 Companies

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/companies/` | List all companies |
| POST | `/api/companies/` | Create company |
| GET/PUT/DELETE | `/api/companies/<id>/` | Manage company |

### 📄 Documents

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET/POST | `/api/tickets-papers/tickets/` | Manage tickets |
| GET/POST | `/api/tickets-papers/traveling-papers/` | Manage papers |

### 🌍 Reference Data

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/core/flags/` | List country flags |
| GET | `/api/core/vessel-types/` | List vessel types |

### 💰 Finance

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET/POST | `/api/finance/finance-records/` | Financial records |

### 🤖 AI Features

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/ai/upload/` | Upload document for AI processing |
| GET | `/ai/applicants/` | List processed applicants |
| POST | `/ai/convert/` | Convert applicant to user |
| POST | `/ai-agents/chat/` | AI chat search |

---

## 📦 Key Data Models

### User (api.Users)

**100+ fields** including:

- Personal: name, age, nationality, marital status
- Contact: email, phone, address
- Documents: passport, seaman book
- Professional: COC, GOC certificates
- Health: medical certificates, vaccinations
- Relationships: certificates, ranks, contracts

### Contract (api.Contract)

Links users to ships with employment details:

- user, ship, rank
- sign_on_date, sign_off_date
- salary, status

### Ship (ships.Ship)

Fleet information:

- ship_name, imo_number
- company, flag, vessel_type
- Technical: tonnage, engine specs
- crew (many-to-many with Users)

### Certificate (api.Certificate)

102 types including:

- STCW Basic Safety courses
- GMDSS, ECDIS, ARPA
- Medical certificates
- Specialized training

### Rank (api.Rank)

51 maritime ranks:

- Deck Officers (Master, Chief Officer, etc.)
- Engine Officers (Chief Engineer, etc.)
- Ratings (Boson, AB, Oiler, etc.)

---

## 🎨 Special Features

### 1. Auto-Generated Rank Codes

When assigning ranks to users, the system automatically generates sequential codes:

- Rank: "DO-1.000" (Master)
- Assigned codes: "DO-1.001", "DO-1.002", "DO-1.003"...

### 2. Calculated Finance Fields

Finance records automatically calculate:

- `total_days` = end_date - start_date
- `daily_rate` = company.hourly_rate × 8
- `total_money` = total_days × daily_rate

### 3. AI Document Processing

Upload a CV/application and the system:

1. Extracts all data using AI
2. Saves to Applicant model
3. Automatically maps to Users model
4. Handles complex field transformations

### 4. Comprehensive User Profiles

Each user can have:

- Multiple certificates (many-to-many)
- Multiple ranks with unique codes
- Multiple contracts (employment history)
- Multiple references
- Multiple sea service records
- Multiple documents (tickets, papers)
- Finance records

---

## 🔍 Filtering Examples

```bash
# Filter users by nationality
GET /api/filter/?nationality=Egypt

# Filter by status
GET /api/filter/?user_status=ON_SITE

# Multiple filters
GET /api/filter/?nationality=Egypt&marital_status=MARRIED&user_status=ON_SITE
```

---

## 📝 Common Workflows

### Workflow 1: Onboard New Seafarer

```bash
# 1. Register user
POST /api/register/
{"email": "...", "password": "...", "first_name": "..."}

# 2. Update profile
PATCH /api/users/<id>/
{...personal details, documents, etc...}

# 3. Add certificates
POST /api/users/<id>/certificates/add/
{"certificate_id": 1}

# 4. Assign rank
POST /api/users/<id>/ranks/add/
{"rank_id": 5}

# 5. Create contract
POST /api/contracts/
{"user_id": ..., "ship_id": ..., "rank_id": ..., ...}
```

### Workflow 2: Process CV with AI

```bash
# 1. Upload document
POST /ai/upload/
[multipart/form-data with PDF/image]

# Returns:
{
  "applicant_id": 25,
  "user_id": 50,
  "message": "Processed successfully"
}

# User is automatically created in the system!
```

### Workflow 3: Track Finances

```bash
# 1. Create finance record
POST /api/finance/finance-records/
{
  "user": 5,
  "company": 2,
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}

# Returns with auto-calculated fields:
{
  "total_days": 31,
  "daily_rate": "200.00",
  "total_money": "6200.00"
}
```

---

## ⚠️ Important Notes

### Authentication

- **Login field is EMAIL** (not username)
- Refresh tokens expire after 15 days
- Include `Authorization: Bearer <token>` in all authenticated requests

### File Uploads

- Use `multipart/form-data` content type
- Supported: PDF, JPEG, PNG
- Files stored in `media/` directory

### Marital Status Choices

- `SINGLE`
- `MARRIED`

### User Status Choices

- `VECATION` (Vacation)
- `ON_SITE`
- `MEDICAL VECATION` (Medical Vacation)

### Contract Status Choices

- `Active`
- `Completed`
- `Pending`

### Company Types

- `Shipping`
- `Cruise`
- `Cargo`
- `Offshore`
- `Other`

---

## 🚀 Installation

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run migrations
python manage.py migrate

# 3. Create superuser (use email!)
python manage.py createsuperuser

# 4. Run server
python manage.py runserver
```

---

## 📚 Documentation Files

1. **API_DOCUMENTATION.md** - Complete API reference (this file's companion)
2. **README.md** - Project overview
3. **This file** - Quick reference guide

---

## 🎯 Next Steps

1. ✅ Read the full **API_DOCUMENTATION.md** for detailed examples
2. ✅ Access Django Admin at `/admin/` for visual management
3. ✅ Test endpoints with Postman or curl
4. ✅ Explore AI document processing features
5. ✅ Set up production database (PostgreSQL)

---

**Need Help?** Check the full API_DOCUMENTATION.md file for:

- Detailed request/response examples
- Error handling guide
- Complete data model specifications
- Architecture diagrams
- Security best practices
