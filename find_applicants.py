"""Look for Documents that would render as 'empty rows' in the Applicants page.

The Document model has its own name/email/phone_number fields separate from
the linked user. The Applicants page likely shows the Document's name,
not the User's. So Documents with empty `name` and no/fake user could
be the source of the 3 empty rows.
"""
import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saker.settings")
django.setup()

from api.models import Document, Users
from django.db.models import Q

print("=== Documents with empty 'name' (the Document's own name field) ===")
empty_name = Document.objects.filter(
    Q(name="") | Q(name__isnull=True)
).select_related("user")
print(f"Count: {empty_name.count()}")
for d in empty_name[:10]:
    print(f"  doc #{d.id} name={d.name!r} title={d.title!r} status={d.status} -> user #{d.user_id} email={d.user.email if d.user_id else 'N/A'}")

print()
print("=== ALL Documents (no name filter) grouped by status ===")
from django.db.models import Count
status_counts = Document.objects.values("status").annotate(c=Count("id"))
for s in status_counts:
    print(f"  {s['status']}: {s['c']}")

print()
print("=== Documents where name is NULL/empty AND user has no first_name (worst case 'Unknown') ===")
worst = Document.objects.filter(
    (Q(name="") | Q(name__isnull=True)),
    (Q(user__first_name="") | Q(user__first_name__isnull=True))
).select_related("user")
print(f"Count: {worst.count()}")
for d in worst[:10]:
    print(f"  doc #{d.id} name={d.name!r} user_first={d.user.first_name if d.user else 'NO_USER'!r}")

print()
print("=== Sample of Documents with no name (regardless of user) ===")
for d in Document.objects.filter(Q(name="") | Q(name__isnull=True))[:5]:
    print(f"  doc #{d.id} name={d.name!r} title={d.title!r} status={d.status} user_id={d.user_id} file={d.file.name if d.file else None}")

print()
print("=== Documents linked to morad@gmail.com (the ahmed morad user from the contract) ===")
try:
    morad = Users.objects.get(email="morad@gmail.com")
    docs = Document.objects.filter(user=morad)
    print(f"User morad: id={morad.id} first_name={morad.first_name!r} middle_name={morad.middle_name!r}")
    print(f"Total docs linked to morad: {docs.count()}")
    for d in docs[:5]:
        print(f"  doc #{d.id} name={d.name!r} title={d.title!r} status={d.status} contract_id={d.contract_id}")
except Users.DoesNotExist:
    print("No user with email morad@gmail.com")
