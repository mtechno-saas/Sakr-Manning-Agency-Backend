"""
Run on server to DELETE UserRank records and custom Rank records
(CUS-*, CLR-*, UNK-*) that were auto-generated during CV ingestion.
Also clears the AI query cache so stale answers are not returned.

Usage:
    cd /opt/sakr/Sakr-Manning-Agency-Backend
    python scratch/clear_rank_codes.py
"""
import os, sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')

from django.conf import settings
settings.LOGGING_CONFIG = None

import django
django.setup()

from api.models import UserRank, Rank

# 1. Delete ALL UserRank records (these hold assigned_code)
ur_count, _ = UserRank.objects.all().delete()
print(f"Deleted {ur_count} UserRank records.")

# 2. Delete custom Rank records (CUS-*, CLR-*, UNK-*)
cus_count, _ = Rank.objects.filter(code__startswith="CUS-").delete()
print(f"Deleted {cus_count} custom Rank records (CUS-*).")

clr_count, _ = Rank.objects.filter(code__startswith="CLR-").delete()
print(f"Deleted {clr_count} custom Rank records (CLR-*).")

unk_count, _ = Rank.objects.filter(code__startswith="UNK-").delete()
print(f"Deleted {unk_count} custom Rank records (UNK-*).")

# 3. Clear AI query cache so stale answers are not returned
try:
    from ai_agents.models import QueryCache
    cache_count, _ = QueryCache.objects.all().delete()
    print(f"Cleared {cache_count} cached AI query results.")
except Exception as e:
    print(f"Could not clear query cache: {e}")

print(f"\nDone! All custom rank entries have been removed.")
