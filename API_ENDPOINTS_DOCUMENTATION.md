# API Endpoints Documentation

## Sakr Manning Agency - Complete API Reference

This document provides a comprehensive list of all API endpoints available in the Sakr Manning Agency backend system.

---

## Table of Contents

- [Authentication Endpoints](#authentication-endpoints)
- [User Management](#user-management)
- [Core Module (Flags & Vessel Types)](#core-module-flags--vessel-types)
- [Ships Management](#ships-management)
- [Companies Management](#companies-management)
- [Tickets & Papers Management](#tickets--papers-management)
- [Finance Management](#finance-management)
- [Interviews Management](#interviews-management)
- [AI Chat Agent](#ai-chat-agent)
- [AI Document Processing](#ai-document-processing)
- [Contracts Management](#contracts-management)
- [Certificates Management](#certificates-management)
- [Ranks Management](#ranks-management)
- [References Management](#references-management)
- [Sea Services Management](#sea-services-management)
- [CV Submissions Management](#cv-submissions-management)

---

## Authentication Endpoints

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/login/` | POST | Obtain JWT access and refresh tokens | AllowAny |
| `/api/login/refresh/` | POST | Refresh JWT access token | AllowAny |
| `/api/register/` | POST | Register a new user account | AllowAny |

---

## User Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/users/` | GET | List all users | IsAuthenticated + UserPermission (Admin/HR/Recruiter: all users, Employee: self only) |
| `/api/users/` | POST | Create a new user | IsAuthenticated + UserPermission (Admin/HR only) |
| `/api/users/{id}/` | GET | Get user details | IsAuthenticated + UserPermission (Admin/HR/Recruiter: all, Employee: self only) |
| `/api/users/{id}/` | PUT | Update user details | IsAuthenticated + UserPermission (Admin/HR: all, Employee: self only) |
| `/api/users/{id}/` | PATCH | Partially update user | IsAuthenticated + UserPermission (Admin/HR: all, Employee: self only) |
| `/api/users/{id}/` | DELETE | Delete a user | IsAuthenticated + UserPermission (Admin only) |
| `/api/users/me/` | GET | Get current authenticated user profile | IsAuthenticated |
| `/api/users/stats/` | GET | Get user statistics for dashboard | IsAuthenticated + UserPermission (Admin/HR only) |
| `/api/all/` | GET | Get all users (alternative endpoint) | IsAuthenticated (Admin/HR/Recruiter only) |
| `/api/create/` | POST | Create user (alternative endpoint) | IsAuthenticated (Admin/HR only) |
| `/api/filter/` | GET | Filter users with query params | IsAuthenticated (Admin/HR/Recruiter only) |
| `/api/users/{pk}/` | GET/PUT/DELETE | User detail operations | Role-based (see permissions) |
| `/api/users/{user_id}/assign-rank/{rank_id}/` | POST | Assign a rank to a user | IsAuthenticated (Admin/HR only) |
| `/api/users/{user_id}/certificates/` | GET | Get all certificates of a user | IsAuthenticated (Owner or Admin/HR/Recruiter) |
| `/api/users/{user_id}/ranks/` | GET | Get all ranks of a user | IsAuthenticated (Owner or Admin/HR/Recruiter) |
| `/api/users/{user_id}/certificates/add/` | POST | Add a certificate to user | IsAuthenticated (Admin/HR only) |
| `/api/users/{user_id}/ranks/add/` | POST | Add a rank to user | IsAuthenticated (Admin/HR only) |
| `/api/users/{user_id}/certificates/{certificate_id}/remove/` | DELETE | Remove certificate from user | IsAuthenticated (Admin/HR only) |
| `/api/users/{user_id}/ranks/{rank_id}/remove/` | DELETE | Remove rank from user | IsAuthenticated (Admin/HR only) |

---

## Core Module (Flags & Vessel Types)

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/core/flags/` | GET | List all flags | IsAuthenticated |
| `/api/core/flags/` | POST | Create a new flag | IsAuthenticated |
| `/api/core/flags/{id}/` | GET | Get flag details | IsAuthenticated |
| `/api/core/flags/{id}/` | PUT | Update flag | IsAuthenticated |
| `/api/core/flags/{id}/` | PATCH | Partially update flag | IsAuthenticated |
| `/api/core/flags/{id}/` | DELETE | Delete a flag | IsAuthenticated |
| `/api/core/vessel-types/` | GET | List all vessel types | IsAuthenticated |
| `/api/core/vessel-types/` | POST | Create a new vessel type | IsAuthenticated |
| `/api/core/vessel-types/{id}/` | GET | Get vessel type details | IsAuthenticated |
| `/api/core/vessel-types/{id}/` | PUT | Update vessel type | IsAuthenticated |
| `/api/core/vessel-types/{id}/` | PATCH | Partially update vessel type | IsAuthenticated |
| `/api/core/vessel-types/{id}/` | DELETE | Delete a vessel type | IsAuthenticated |

---

## Ships Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/ships/` | GET | List all ships | IsAuthenticated + IsShipManagerOrAdmin |
| `/api/ships/` | POST | Create a new ship | IsAuthenticated + IsShipManagerOrAdmin |
| `/api/ships/{id}/` | GET | Get ship details | IsAuthenticated + IsShipManagerOrAdmin |
| `/api/ships/{id}/` | PUT | Update ship | IsAuthenticated + IsShipManagerOrAdmin |
| `/api/ships/{id}/` | PATCH | Partially update ship | IsAuthenticated + IsShipManagerOrAdmin |
| `/api/ships/{id}/` | DELETE | Delete a ship | IsAuthenticated + IsShipManagerOrAdmin |
| `/api/ships/{id}/assign-user/` | POST | Assign a user to ship's crew | IsAuthenticated + IsShipManagerOrAdmin |
| `/api/ships/{id}/unassign-user/` | POST | Remove a user from ship's crew | IsAuthenticated + IsShipManagerOrAdmin |

---

## Companies Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/companies/` | GET | List all companies | IsAuthenticated + CompanyPermission (All can read) |
| `/api/companies/` | POST | Create a new company | IsAuthenticated + CompanyPermission (Admin only) |
| `/api/companies/{id}/` | GET | Get company details | IsAuthenticated + CompanyPermission (All can read) |
| `/api/companies/{id}/` | PUT | Update company | IsAuthenticated + CompanyPermission (Admin/HR/Recruiter) |
| `/api/companies/{id}/` | PATCH | Partially update company | IsAuthenticated + CompanyPermission (Admin/HR/Recruiter) |
| `/api/companies/{id}/` | DELETE | Delete a company | IsAuthenticated + CompanyPermission (Admin only) |
| `/api/companies/stats/` | GET | Get companies statistics | IsAuthenticated + CompanyPermission |

---

## Tickets & Papers Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/tickets-papers/tickets/` | GET | List all tickets | IsAuthenticated |
| `/api/tickets-papers/tickets/` | POST | Create a new ticket | IsAuthenticated |
| `/api/tickets-papers/tickets/{id}/` | GET | Get ticket details | IsAuthenticated |
| `/api/tickets-papers/tickets/{id}/` | PUT | Update ticket | IsAuthenticated |
| `/api/tickets-papers/tickets/{id}/` | PATCH | Partially update ticket | IsAuthenticated |
| `/api/tickets-papers/tickets/{id}/` | DELETE | Delete a ticket | IsAuthenticated |
| `/api/tickets-papers/traveling-papers/` | GET | List all traveling papers | IsAuthenticated |
| `/api/tickets-papers/traveling-papers/` | POST | Create a new traveling paper | IsAuthenticated |
| `/api/tickets-papers/traveling-papers/{id}/` | GET | Get traveling paper details | IsAuthenticated |
| `/api/tickets-papers/traveling-papers/{id}/` | PUT | Update traveling paper | IsAuthenticated |
| `/api/tickets-papers/traveling-papers/{id}/` | PATCH | Partially update traveling paper | IsAuthenticated |
| `/api/tickets-papers/traveling-papers/{id}/` | DELETE | Delete a traveling paper | IsAuthenticated |

---

## Finance Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/finance/finance-records/` | GET | List all finance records | IsAuthenticated + FinancePermission (Admin/HR: all, Others: own only) |
| `/api/finance/finance-records/` | POST | Create a new finance record | IsAuthenticated + FinancePermission (Admin/HR only) |
| `/api/finance/finance-records/{id}/` | GET | Get finance record details | IsAuthenticated + FinancePermission (Admin/HR: all, Owner: own) |
| `/api/finance/finance-records/{id}/` | PUT | Update finance record | IsAuthenticated + FinancePermission (Admin/HR only) |
| `/api/finance/finance-records/{id}/` | PATCH | Partially update finance record | IsAuthenticated + FinancePermission (Admin/HR only) |
| `/api/finance/finance-records/{id}/` | DELETE | Delete a finance record | IsAuthenticated + FinancePermission (Admin/HR only) |
| `/api/finance/finance-records/calculate/` | POST | Calculate finance without saving | IsAuthenticated + FinancePermission |
| `/api/finance/finance-records/stats/` | GET | Get finance statistics | IsAuthenticated + FinancePermission (Admin/HR only) |
| `/api/finance/finance-records/export/` | GET | Export finance records | IsAuthenticated + FinancePermission (Admin/HR only) |

---

## Interviews Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/interviews/interviews/` | GET | List all interviews | IsAuthenticated + InterviewPermission (Admin/HR/Recruiter: all, Employee: own) |
| `/api/interviews/interviews/` | POST | Create a new interview | IsAuthenticated + InterviewPermission (Admin/HR/Recruiter only) |
| `/api/interviews/interviews/{id}/` | GET | Get interview details | IsAuthenticated + InterviewPermission (Admin/HR/Recruiter: all, Candidate: own) |
| `/api/interviews/interviews/{id}/` | PUT | Update interview | IsAuthenticated + InterviewPermission (Admin/HR/Recruiter only) |
| `/api/interviews/interviews/{id}/` | PATCH | Partially update interview | IsAuthenticated + InterviewPermission (Admin/HR/Recruiter only) |
| `/api/interviews/interviews/{id}/` | DELETE | Delete an interview | IsAuthenticated + InterviewPermission (Admin/HR/Recruiter only) |
| `/api/interviews/interviews/stats/` | GET | Get interview statistics | IsAuthenticated + InterviewPermission |
| `/api/interviews/interviews/calendar/` | GET | Get interviews for calendar view | IsAuthenticated + InterviewPermission |

---

## AI Chat Agent

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/ai-agents/chat/` | POST | Send a message to AI chat agent | AllowAny |
| `/ai-agents/chat/history/{session_id}/` | GET | Get chat history for a session | AllowAny |
| `/ai-agents/chat/sessions/` | GET | Get all user sessions | IsAuthenticated |
| `/ai-agents/capabilities/` | GET | Get AI search capabilities info | AllowAny |

---

## AI Document Processing

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/ai/upload/` | POST | Upload and process document (PDF/DOCX), extract data to Applicant & Users | IsAuthenticated |
| `/ai/applicants/` | GET | List all applicants | IsAuthenticated |
| `/ai/applicants/{applicant_id}/` | GET | Get detailed applicant information | IsAuthenticated |
| `/ai/convert/` | POST | Convert an applicant to a user | IsAuthenticated |
| `/ai/batch-convert/` | POST | Convert multiple applicants to users | IsAuthenticated |
| `/ai/sync-status/` | GET | Check sync status between Applicant and Users models | IsAuthenticated |

---

## Contracts Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/contracts/` | GET | List all contracts | IsAuthenticated + ContractPermission (Admin/HR/Recruiter: all, Employee: own) |
| `/api/contracts/` | POST | Create a new contract | IsAuthenticated + ContractPermission (Admin/HR only) |
| `/api/contracts/{id}/` | GET | Get contract details | IsAuthenticated + ContractPermission (Admin/HR/Recruiter: all, Owner: own) |
| `/api/contracts/{id}/` | PUT | Update contract | IsAuthenticated + ContractPermission (Admin/HR only) |
| `/api/contracts/{id}/` | PATCH | Partially update contract | IsAuthenticated + ContractPermission (Admin/HR only) |
| `/api/contracts/{id}/` | DELETE | Delete a contract | IsAuthenticated + ContractPermission (Admin/HR only) |
| `/api/contracts/stats/` | GET | Get contract statistics | IsAuthenticated + ContractPermission |

---

## Certificates Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/certificates/` | GET | List all certificates | IsAuthenticated + IsHROrReadOnly (All can read) |
| `/api/certificates/` | POST | Create a new certificate | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/certificates/{id}/` | GET | Get certificate details | IsAuthenticated + IsHROrReadOnly (All can read) |
| `/api/certificates/{id}/` | PUT | Update certificate | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/certificates/{id}/` | PATCH | Partially update certificate | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/certificates/{id}/` | DELETE | Delete a certificate | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |

---

## Ranks Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/ranks/` | GET | List all ranks | IsAuthenticated + IsHROrReadOnly (All can read) |
| `/api/ranks/` | POST | Create a new rank | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/ranks/{id}/` | GET | Get rank details | IsAuthenticated + IsHROrReadOnly (All can read) |
| `/api/ranks/{id}/` | PUT | Update rank | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/ranks/{id}/` | PATCH | Partially update rank | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/ranks/{id}/` | DELETE | Delete a rank | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |

---

## References Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/references/` | GET | List all references | IsAuthenticated + IsHROrReadOnly (All can read) |
| `/api/references/` | POST | Create a new reference | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/references/{id}/` | GET | Get reference details | IsAuthenticated + IsHROrReadOnly (All can read) |
| `/api/references/{id}/` | PUT | Update reference | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/references/{id}/` | PATCH | Partially update reference | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/references/{id}/` | DELETE | Delete a reference | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |

---

## Sea Services Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/sea-services/` | GET | List all sea services | IsAuthenticated + IsHROrReadOnly (All can read) |
| `/api/sea-services/` | POST | Create a new sea service | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/sea-services/{id}/` | GET | Get sea service details | IsAuthenticated + IsHROrReadOnly (All can read) |
| `/api/sea-services/{id}/` | PUT | Update sea service | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/sea-services/{id}/` | PATCH | Partially update sea service | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |
| `/api/sea-services/{id}/` | DELETE | Delete a sea service | IsAuthenticated + IsHROrReadOnly (Admin/HR only) |

---

## CV Submissions Management

| Endpoint | Method | Description | Permissions |
|----------|--------|-------------|-------------|
| `/api/cv-submissions/` | GET | List all CV submissions | IsAuthenticated + CVPermission (Admin/HR/Recruiter: all, Employee: own) |
| `/api/cv-submissions/` | POST | Submit a new CV | IsAuthenticated + CVPermission (Admin/HR: any user, Employee: self only) |
| `/api/cv-submissions/{id}/` | GET | Get CV submission details | IsAuthenticated + CVPermission (Admin/HR/Recruiter: all, Owner: own) |
| `/api/cv-submissions/{id}/` | PUT | Update CV submission | IsAuthenticated + CVPermission (Admin/HR only) |
| `/api/cv-submissions/{id}/` | PATCH | Partially update CV submission | IsAuthenticated + CVPermission (Admin/HR/Recruiter) |
| `/api/cv-submissions/{id}/` | DELETE | Delete a CV submission | IsAuthenticated + CVPermission (Admin/HR only) |
| `/api/cv-submissions/stats/` | GET | Get CV statistics for dashboard | IsAuthenticated + CVPermission |
| `/api/cv-submissions/{id}/update-status/` | PATCH | Update CV status | IsAuthenticated + CVPermission (Admin/HR/Recruiter only) |

---

## Permission Roles Summary

The system uses role-based permissions with the following roles:

| Role | Description | Access Level |
|------|-------------|--------------|
| **Admin** | System Administrator | Full access to all resources |
| **HR Manager** | Human Resources Manager | Can manage all resources except Admin-level operations |
| **Recruiter** | Recruitment Specialist | Can view most resources, edit candidates and CV submissions |
| **Employee** | Regular Employee | Can only view/edit own profile and submissions |

### Permission Classes

- **AllowAny**: No authentication required
- **IsAuthenticated**: Requires valid JWT token
- **UserPermission**: Role-based access for user management
- **CompanyPermission**: Role-based access for companies (Admin: full, HR/Recruiter: edit, Employee: read)
- **InterviewPermission**: Admin/HR/Recruiter have full access, Employee can view own interviews
- **FinancePermission**: Admin/HR have full access, others can view own records
- **CVPermission**: Admin/HR have full access, Recruiter can view/update status, Employee can submit/view own
- **ContractPermission**: Admin/HR have full access, others can view own contracts
- **IsHROrReadOnly**: HR/Admin can edit, others have read-only access
- **IsOwnerOrHR**: Users can access own data, HR/Admin can access all
- **IsShipManagerOrAdmin**: Ship Managers and Admins have full access

---

## Notes

1. **Authentication**: All endpoints (except those marked with `AllowAny`) require JWT authentication via the `Authorization: Bearer <token>` header.

2. **Standard REST Methods**:
   - `GET` - Retrieve resource(s)
   - `POST` - Create new resource
   - `PUT` - Full update of resource
   - `PATCH` - Partial update of resource
   - `DELETE` - Delete resource

3. **Filtering**: Many list endpoints support filtering via query parameters. Check individual serializers and filterset classes for available filters.

4. **Pagination**: List endpoints typically support pagination. Use `?page=<number>` query parameter.

5. **Special Actions**: Endpoints with `/stats/`, `/calculate/`, `/calendar/`, etc. are custom actions providing additional functionality beyond standard CRUD operations.

6. **Media Files**: Some endpoints accept file uploads (multipart/form-data), particularly for documents, photos, CVs, tickets, and traveling papers.

---

**Last Updated**: December 2025  
**Version**: 1.0  
**Project**: Sakr Manning Agency Backend System
