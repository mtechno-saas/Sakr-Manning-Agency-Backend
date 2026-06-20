"""Smoke test: import all filter classes and instantiate them against an empty
QueryDict to make sure none of them blow up at construction time.

Run from the project root:
    python test_filters_smoke.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saker.settings")
django.setup()

from django.http import QueryDict

from api.filters import (
    UsersFilter,
    CompanyFilter as ApiCompanyFilter,        # not routed, but still importable
    InterviewFilter,
    FinanceRecordFilter,
    CVSubmissionFilter,
    JobOrderFilter,
    FlightBookingFilter,
    VisaApplicationFilter,
    AuditFilter,
    IncidentReportFilter,
    ShipFilter,
    ContractFilter,
)
from companies.filters import CompanyFilter as CompaniesCompanyFilter
from api.models import Users, Company as ApiCompany, Interview, CVSubmission, Contract
from compliance.models import Audit, IncidentReport
from finance.models import FinanceRecord
from companies.models import Company as CompaniesCompany, JobOrder
from logistics.models import FlightBooking, VisaApplication
from ships.models import Ship


def try_instantiate(name, FilterClass, model):
    try:
        f = FilterClass(QueryDict(""), queryset=model.objects.all())
        f.is_valid()  # forces form validation
        qs = f.qs     # forces filter_queryset (exercises distinct override)
        print(f"  [OK]  {name:<35} -> {qs.query}")
    except Exception as e:
        print(f"  [FAIL] {name}: {type(e).__name__}: {e}")
        raise


def main():
    print("Smoke-testing every FilterSet with an empty QueryDict...\n")
    try_instantiate("UsersFilter",              UsersFilter,              Users)
    try_instantiate("ApiCompanyFilter (dead)",  ApiCompanyFilter,         ApiCompany)
    try_instantiate("InterviewFilter",          InterviewFilter,          Interview)
    try_instantiate("FinanceRecordFilter",      FinanceRecordFilter,      FinanceRecord)
    try_instantiate("CVSubmissionFilter",       CVSubmissionFilter,       CVSubmission)
    try_instantiate("JobOrderFilter",           JobOrderFilter,           JobOrder)
    try_instantiate("FlightBookingFilter",      FlightBookingFilter,      FlightBooking)
    try_instantiate("VisaApplicationFilter",    VisaApplicationFilter,    VisaApplication)
    try_instantiate("AuditFilter",              AuditFilter,              Audit)
    try_instantiate("IncidentReportFilter",     IncidentReportFilter,     IncidentReport)
    try_instantiate("ShipFilter",               ShipFilter,               Ship)
    try_instantiate("ContractFilter",           ContractFilter,           Contract)
    try_instantiate("CompaniesCompanyFilter",   CompaniesCompanyFilter,   CompaniesCompany)

    print("\nAll filters instantiated and validated cleanly.")


if __name__ == "__main__":
    main()
