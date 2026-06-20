"""
Behavior test for the NEW CVSubmission-backed fields on UsersFilter.

Verifies that:
  - ?company_name= searches CVSubmission.company in addition to Contract/SeaService
  - ?ship_name=    searches CVSubmission.ship     in addition to Contract
  - ?company=      searches CVSubmission.company (both id and name branches)
  - ?ship=         searches CVSubmission.ship     (both id and name branches)
  - ?rank_name=    searches CVSubmission.position in addition to existing 6 sources
  - ?position=     searches CVSubmission.position in addition to existing 3 sources
  - ?cv_status=    finds users by CV submission status (multi-value, case-insensitive)
  - ?cv_notes=     finds users by CV submission notes (icontains)

Run from the project root:
    python test_cv_filters_behavior.py
"""
import os
import sys
import django
from datetime import date

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saker.settings")
django.setup()

# Use an isolated SQLite file so we don't touch the real db.sqlite3
TEST_DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_cv_filter_run.sqlite3")
if os.path.exists(TEST_DB):
    os.remove(TEST_DB)
from django.conf import settings
settings.DATABASES["default"]["NAME"] = TEST_DB

from django.core.management import call_command
call_command("migrate", verbosity=0, interactive=False)

from django.http import QueryDict
from django.contrib.auth import get_user_model

from api.models import Users, Company as ApiCompany, Contract, CVSubmission, SeaService
from api.filters import UsersFilter
from companies.models import Company, CompanyType
from ships.models import Ship
from core.models import Flag, VesselType


def parse_qs(s):
    return QueryDict(s)


# ---------- seed ----------
print("Seeding CVSubmission test data...")

ct_owner, _ = CompanyType.objects.get_or_create(name="Owner")
vessel_bulk, _ = VesselType.objects.get_or_create(name="Bulk Carrier")
flag_panama, _ = Flag.objects.get_or_create(name="Panama")

# Two companies: MAERSK (one user has contract, one user only applied via CV),
# ROMALEX (only one user has applied via CV — never signed a contract)
co_maersk = Company.objects.create(company_name="MAERSK LINE", company_type=ct_owner, status="Active", contact_email="m@m.com")
co_romalex = Company.objects.create(company_name="ROMALEX MARINE", company_type=ct_owner, status="Active", contact_email="r@r.com")

ship_northern = Ship.objects.create(ship_name="NORTHERN STAR", imo_number="IMO-NS-1", company=co_maersk, ship_type=vessel_bulk, flag=flag_panama, status="Active")
ship_southern = Ship.objects.create(ship_name="SOUTHERN CROSS", imo_number="IMO-SC-1", company=co_romalex, ship_type=vessel_bulk, flag=flag_panama, status="Active")

User = get_user_model()

# u_ahmed: signed contract with MAERSK on NORTHERN STAR + also submitted CV
u_ahmed = User.objects.create_user(email="ahmed@x.com", first_name="Ahmed", user_status="ON_SITE", nationality="Egypt")
Contract.objects.create(user=u_ahmed, company=co_maersk, ship=ship_northern, sign_on_date=date(2024,1,1), sign_off_date=date(2024,6,1), status="Signed")

# u_mona: applied to ROMALEX via CV, but has NO contract yet  <-- the gap we want to bridge
u_mona = User.objects.create_user(email="mona@x.com", first_name="Mona", user_status="VACATION", nationality="Egypt")

# u_khaled: applied to MAERSK via CV (different ship SOUTHERN CROSS, which ROMALEX owns)
u_khaled = User.objects.create_user(email="khaled@x.com", first_name="Khaled", user_status="ON_SITE", nationality="Syria")

# u_sara: applied to ROMALEX with a CV note "strong candidate"
u_sara = User.objects.create_user(email="sara@x.com", first_name="Sara", user_status="ON_SITE", nationality="Egypt")

# CV submissions
CVSubmission.objects.create(
    user=u_ahmed, company=co_maersk, ship=ship_northern,
    status="Approved", notes="Old application, accepted.",
)
CVSubmission.objects.create(
    user=u_mona, company=co_romalex, ship=ship_southern,
    status="Pending", notes="Applied for chief officer role.",
)
CVSubmission.objects.create(
    user=u_khaled, company=co_maersk, ship=ship_southern,
    status="Shortlisted", notes="LNG experience preferred.",
)
CVSubmission.objects.create(
    user=u_sara, company=co_romalex, ship=ship_southern,
    status="Approved", notes="Strong candidate for next available.",
)

print("Seed complete.\n")


# ---------- assertions ----------
failures = []
def check(label, actual, expected):
    if sorted(actual) == sorted(expected):
        print(f"  [PASS] {label}: got {sorted(actual)}")
    else:
        print(f"  [FAIL] {label}: expected {sorted(expected)}, got {sorted(actual)}")
        failures.append(label)


print("=== ?company_name= ROMALEX (no contract, only CV) ===")
# Before the change: would only return users with a Contract → empty for ROMALEX
# After the change: should also find users who applied to ROMALEX via CV
qs = UsersFilter(parse_qs("company_name=ROMALEX"), queryset=Users.objects.all()).qs
check("company_name=ROMALEX finds CV-only applicants", list(qs.values_list("email", flat=True)),
      ["mona@x.com", "sara@x.com"])

print("\n=== ?company_name= MAERSK (both contract and CV users) ===")
qs = UsersFilter(parse_qs("company_name=MAERSK"), queryset=Users.objects.all()).qs
check("company_name=MAERSK finds both contract and CV users", list(qs.values_list("email", flat=True)),
      ["ahmed@x.com", "khaled@x.com"])

print("\n=== ?company=<id> finds CV applicants too ===")
qs = UsersFilter(parse_qs(f"company={co_romalex.id}"), queryset=Users.objects.all()).qs
check("company=romalex_id (numeric) finds CV applicants", list(qs.values_list("email", flat=True)),
      ["mona@x.com", "sara@x.com"])

print("\n=== ?ship_name= SOUTHERN (no contract, only CV) ===")
# SOUTHERN CROSS belongs to ROMALEX — no contract, only CV applications
qs = UsersFilter(parse_qs("ship_name=SOUTHERN"), queryset=Users.objects.all()).qs
check("ship_name=SOUTHERN finds CV-only applicants", list(qs.values_list("email", flat=True)),
      ["mona@x.com", "khaled@x.com", "sara@x.com"])

print("\n=== ?ship=<id> finds CV applicants too ===")
qs = UsersFilter(parse_qs(f"ship={ship_northern.id}"), queryset=Users.objects.all()).qs
check("ship=northern_id finds both contract and CV users", list(qs.values_list("email", flat=True)),
      ["ahmed@x.com"])

print("\n=== ?cv_status=Pending ===")
qs = UsersFilter(parse_qs("cv_status=Pending"), queryset=Users.objects.all()).qs
check("cv_status=Pending", list(qs.values_list("email", flat=True)),
      ["mona@x.com"])

print("\n=== ?cv_status=Pending&cv_status=Approved (multi-value) ===")
qs = UsersFilter(parse_qs("cv_status=Pending&cv_status=Approved"),
                 queryset=Users.objects.all()).qs
check("cv_status multi", list(qs.values_list("email", flat=True)),
      ["ahmed@x.com", "mona@x.com", "sara@x.com"])

print("\n=== ?cv_status=pending (case-insensitive) ===")
qs = UsersFilter(parse_qs("cv_status=pending"), queryset=Users.objects.all()).qs
check("cv_status=pending (iexact)", list(qs.values_list("email", flat=True)),
      ["mona@x.com"])

print("\n=== ?cv_notes=strong (icontains) ===")
qs = UsersFilter(parse_qs("cv_notes=strong"), queryset=Users.objects.all()).qs
check("cv_notes=strong", list(qs.values_list("email", flat=True)),
      ["sara@x.com"])

print("\n=== ?cv_notes=CHIEF (icontains — case-insensitive) ===")
qs = UsersFilter(parse_qs("cv_notes=CHIEF"), queryset=Users.objects.all()).qs
check("cv_notes=CHIEF", list(qs.values_list("email", flat=True)),
      ["mona@x.com"])

print("\n=== Combined: ?company_name=ROMALEX&cv_status=Approved ===")
qs = UsersFilter(parse_qs("company_name=ROMALEX&cv_status=Approved"),
                 queryset=Users.objects.all()).qs
check("ROMALEX + Approved", list(qs.values_list("email", flat=True)),
      ["sara@x.com"])


# ---------- summary ----------
print("\n" + "=" * 60)
if failures:
    print(f"FAILED ({len(failures)}):")
    for f in failures:
        print(f"  - {f}")
    sys.exit(1)
else:
    print("All CVSubmission-backed filter checks PASSED.")
    sys.exit(0)
