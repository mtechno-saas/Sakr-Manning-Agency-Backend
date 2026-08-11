"""Inspect Documents on production to find what the 3 empty rows actually are."""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saker.settings")
django.setup()

from api.models import Document, Users
from django.db.models import Q

print("=== Documents with user_id IS NULL ===")
null_user_docs = Document.objects.filter(user__isnull=True)
print(f"Count: {null_user_docs.count()}")
for d in null_user_docs[:10]:
    print(f"  doc #{d.id} title={d.title!r} file={d.file.name if d.file else None} status={d.status} user_id={d.user_id} contract_id={d.contract_id} created={d.created_at}")

print()
print("=== Documents linked to users with empty first_name ===")
empty_name_docs = Document.objects.filter(
    Q(user__isnull=False) & (Q(user__first_name="") | Q(user__first_name__isnull=True))
).select_related("user")
print(f"Count: {empty_name_docs.count()}")
for d in empty_name_docs[:10]:
    print(f"  doc #{d.id} title={d.title!r} status={d.status} -> user #{d.user_id} email={d.user.email!r} first={d.user.first_name!r} middle={d.user.middle_name!r}")

print()
print("=== All Users with email like applicant_<hex>@placeholder... ===")
import re
ps = Users.objects.filter(email__regex=r"^applicant_[0-9a-f]{8}@placeholder\.sakrshipping\.com$")
print(f"Count: {ps.count()}")
for u in ps[:10]:
    print(f"  user #{u.id} email={u.email} first={u.first_name!r} docs={u.documents.count()}")

print()
print("=== Users with no first_name OR no last_name, no Applicant CVs ===")
weird = Users.objects.filter(
    Q(first_name__regex=r"^Applicant") | Q(first_name="") | Q(first_name__isnull=True)
)
print(f"Count: {weird.count()}")
for u in weird[:10]:
    print(f"  user #{u.id} email={u.email} first={u.first_name!r} middle={u.middle_name!r} docs={u.documents.count()}")
