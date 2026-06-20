"""
Behavioural test: spin up a clean SQLite test DB, seed it, then run the
filter query strings documented in global_filters_reference.md and assert
the filters actually do what the doc says.

Run from the project root:
    python test_filters_behavior.py
"""
import os
import sys
import django
from datetime import date, timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saker.settings")
django.setup()

# Use an isolated SQLite file so we don't touch the real db.sqlite3
TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_filter_run.sqlite3")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
from django.conf import settings
settings.DATABASES["default"]["NAME"] = TEST_DB

from django.core.management import call_command
call_command("migrate", verbosity=0, interactive=False)

from django.test.utils import setup_test_environment, teardown_test_environment
from django.test import Client
from django.contrib.auth import get_user_model

from django.http import QueryDict
from api.models import (
    Users, Company as ApiCompany, Contract, CVSubmission,
    PersonalDocument, Document, UserLanguage, LanguageProficiency,
)
from api.filters import UsersFilter
from companies.models import Company, CompanyType, JobOrder
from companies.filters import CompanyFilter as CompaniesCompanyFilter
from ships.models import Ship
from core.models import Flag, VesselType
from compliance.models import IncidentReport, Audit


# ---------- helpers ----------
def parse_qs(s):
    """Parse a querystring into QueryDict, preserving repeated keys."""
    qd = QueryDict(s)
    return qd


# ---------- seed data ----------
print("Seeding test data...")

# core lookups — use get_or_create so we survive repeated runs / pre-existing seeds
ct_agency, _ = CompanyType.objects.get_or_create(name="Agency")
ct_owner, _ = CompanyType.objects.get_or_create(name="Owner")
ct_other, _ = CompanyType.objects.get_or_create(name="Other")

vessel_bulk, _ = VesselType.objects.get_or_create(name="Bulk Carrier")
vessel_tanker, _ = VesselType.objects.get_or_create(name="Tanker")
flag_panama, _ = Flag.objects.get_or_create(name="Panama")
flag_bahamas, _ = Flag.objects.get_or_create(name="Bahamas")

# companies (2 in each company_type)
co_agency_a = Company.objects.create(
    company_name="Maersk Agency", company_type=ct_agency, contact_email="a@m.com",
    status="Active",
)
co_agency_b = Company.objects.create(
    company_name="PIL Agency", company_type=ct_agency, contact_email="b@p.com",
    status="Inactive",
)
co_owner_a = Company.objects.create(
    company_name="Maersk Owner", company_type=ct_owner, contact_email="c@m.com",
    status="Active",
)
co_owner_b = Company.objects.create(
    company_name="PIL Owner", company_type=ct_owner, contact_email="d@p.com",
    status="Prospect",
)
co_other = Company.objects.create(
    company_name="Misc Co", company_type=ct_other, contact_email="e@x.com",
    status="Active",
)

# ships
ship_a = Ship.objects.create(
    ship_name="Northern Star", imo_number="IMO-001", company=co_owner_a,
    ship_type=vessel_bulk, flag=flag_panama, status="Active",
)
ship_b = Ship.objects.create(
    ship_name="Eastern Wind", imo_number="IMO-002", company=co_owner_b,
    ship_type=vessel_tanker, flag=flag_bahamas, status="Active",
)

# users (4 with predictable names)
User = get_user_model()
u1 = User.objects.create_user(email="ahmed@x.com", first_name="Ahmed", middle_name="Hassan",
                              user_status="ON_SITE", nationality="Egypt", role="Employee")
u2 = User.objects.create_user(email="mohamed@x.com", first_name="Mohamed", middle_name="Ali",
                              user_status="VACATION", nationality="Syria", role="Employee")
u3 = User.objects.create_user(email="sara@x.com", first_name="Sara", middle_name="Khaled",
                              user_status="ON_SITE", nationality="Egypt", role="Recruiter")
u4 = User.objects.create_user(email="john@x.com", first_name="John", middle_name="Smith",
                              user_status="ON_SITE", nationality="USA", role="Employee")

# Contracts — u1 has TWO contracts with co_agency_a to test the M2M distinct fix
Contract.objects.create(user=u1, company=co_agency_a, ship=ship_a,
                        sign_on_date=date(2024, 1, 1), sign_off_date=date(2024, 6, 1),
                        status="Signed")
Contract.objects.create(user=u1, company=co_agency_a, ship=ship_b,
                        sign_on_date=date(2024, 6, 2), sign_off_date=date(2024, 12, 1),
                        status="Active")
Contract.objects.create(user=u2, company=co_owner_b, ship=ship_b,
                        sign_on_date=date(2024, 3, 1), sign_off_date=date(2024, 9, 1),
                        status="Active")
Contract.objects.create(user=u3, company=co_owner_a, ship=ship_a,
                        sign_on_date=date(2024, 5, 1), sign_off_date=date(2024, 11, 1),
                        status="Draft")

# Personal documents — different types per user
PersonalDocument.objects.create(user=u1, document_type="Passport", document_number="P-001")
PersonalDocument.objects.create(user=u1, document_type="Panama Seaman's Book", document_number="SB-001")
PersonalDocument.objects.create(user=u2, document_type="Bahamas Seaman's Book", document_number="SB-002")
PersonalDocument.objects.create(user=u4, document_type="Schengen Visa", document_number="V-001")

# Document (status filter)
Document.objects.create(user=u3, title="CV John", status="Active")
Document.objects.create(user=u3, title="CV Ahmed", status="Pending")

# Incident report
IncidentReport.objects.create(
    title="Engine failure", incident_type="Accident", severity="High",
    ship=ship_a, is_closed=False, date_occurred=date(2024, 5, 1),
)
IncidentReport.objects.create(
    title="Crew complaint", incident_type="Grievance", severity="Low",
    ship=ship_b, is_closed=True, date_occurred=date(2024, 6, 1),
)

print("Seed complete.\n")


# ---------- assertion helpers ----------
failures = []
def check(label, actual, expected):
    if actual == expected:
        print(f"  [PASS] {label}: got {actual}")
    else:
        print(f"  [FAIL] {label}: expected {expected}, got {actual}")
        failures.append(label)


# ============================================================
# Test 1: CompanyFilter multi-value
# ============================================================
print("=== CompanyFilter ===")
# ?company_type=Agency&company_type=Owner  -> 4 companies (agency_a, agency_b, owner_a, owner_b)
qs = CompaniesCompanyFilter(parse_qs("company_type=Agency&company_type=Owner"), queryset=Company.objects.all()).qs
check("multi company_type", sorted(qs.values_list("company_name", flat=True)),
      ["Maersk Agency", "Maersk Owner", "PIL Agency", "PIL Owner"])

# ?status=Active&status=Inactive  -> 4 companies (3 Active + 1 Inactive; PIL Owner is Prospect)
qs = CompaniesCompanyFilter(parse_qs("status=Active&status=Inactive"), queryset=Company.objects.all()).qs
check("multi status", sorted(qs.values_list("company_name", flat=True)),
      ["Maersk Agency", "Maersk Owner", "Misc Co", "PIL Agency"])

# ?name=maersk  -> 2 companies (case-insensitive contains)
qs = CompaniesCompanyFilter(parse_qs("name=maersk"), queryset=Company.objects.all()).qs
check("name icontains", sorted(qs.values_list("company_name", flat=True)),
      ["Maersk Agency", "Maersk Owner"])


# ============================================================
# Test 2: UsersFilter M2M distinct
# ============================================================
print("\n=== UsersFilter (M2M distinct) ===")
# u1 has TWO contracts with co_agency_a; without distinct we would get 2 rows for u1
qs = UsersFilter(parse_qs("company=1"), queryset=Users.objects.all()).qs
# co_agency_a is the first company created -> its id should be 1
agency_a_id = co_agency_a.id
qs = UsersFilter(parse_qs(f"company={agency_a_id}"), queryset=Users.objects.all()).qs
check("company=agency_a returns unique users", sorted(qs.values_list("email", flat=True)),
      ["ahmed@x.com"])

# Without distinct, contract_status filter would also duplicate u1
qs = UsersFilter(parse_qs("contract_status=Signed&contract_status=Active"),
                 queryset=Users.objects.all()).qs
check("contract_status multi no duplicates", sorted(qs.values_list("email", flat=True)),
      ["ahmed@x.com", "mohamed@x.com"])


# ============================================================
# Test 3: UsersFilter passport_type / seaman_book_type
# ============================================================
print("\n=== UsersFilter (passport / seaman book) ===")
qs = UsersFilter(parse_qs("passport_type=Passport"), queryset=Users.objects.all()).qs
check("passport_type=Passport", sorted(qs.values_list("email", flat=True)),
      ["ahmed@x.com"])

qs = UsersFilter(parse_qs("seaman_book_type=Panama"), queryset=Users.objects.all()).qs
check("seaman_book_type=Panama", sorted(qs.values_list("email", flat=True)),
      ["ahmed@x.com"])


# ============================================================
# Test 4: UsersFilter document_status
# ============================================================
print("\n=== UsersFilter (document_status / document_title) ===")
qs = UsersFilter(parse_qs("document_status=Active"), queryset=Users.objects.all()).qs
check("document_status=Active", sorted(qs.values_list("email", flat=True)),
      ["sara@x.com"])


# ============================================================
# Test 5: IncidentReportFilter (must not crash)
# ============================================================
print("\n=== IncidentReportFilter ===")
from api.filters import IncidentReportFilter
qs = IncidentReportFilter(parse_qs("incident_type=Accident"), queryset=IncidentReport.objects.all()).qs
check("incident_type=Accident", qs.count(), 1)
qs = IncidentReportFilter(parse_qs("is_closed=true"), queryset=IncidentReport.objects.all()).qs
check("is_closed=true", qs.count(), 1)


# ============================================================
# Test 6: User nationality + status multi
# ============================================================
print("\n=== UsersFilter (multi nationality / user_status) ===")
qs = UsersFilter(parse_qs("nationality=Egypt&nationality=Syria"),
                 queryset=Users.objects.all()).qs
check("multi nationality", sorted(qs.values_list("email", flat=True)),
      ["ahmed@x.com", "mohamed@x.com", "sara@x.com"])


# ---------- summary ----------
print("\n" + "=" * 60)
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("All behaviour checks PASSED.")
    sys.exit(0)
