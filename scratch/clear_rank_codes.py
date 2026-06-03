"""
Run on server to clear assigned_code from UserRank records
and rank_code (Rank.code) for all custom-generated (CUS-*) ranks.

Usage:
    cd /opt/sakr/Sakr-Manning-Agency-Backend
    python scratch/clear_rank_codes.py
"""
import os, sys, uuid

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')

from django.conf import settings
settings.LOGGING_CONFIG = None

import django
django.setup()

from api.models import UserRank, Rank

# 1. Clear all assigned_code values on UserRank
ur_count = UserRank.objects.exclude(assigned_code="").update(assigned_code="")
print(f"Cleared assigned_code on {ur_count} UserRank records.")

# 2. Clear rank codes that start with "CUS-" (auto-generated during ingestion)
#    Since Rank.code has a UNIQUE constraint, we replace each with a unique placeholder
cus_ranks = Rank.objects.filter(code__startswith="CUS-")
cus_count = 0
for rank in cus_ranks:
    rank.code = f"CLR-{uuid.uuid4().hex[:8].upper()}"
    rank.save(update_fields=['code'])
    cus_count += 1
print(f"Cleared rank_code on {cus_count} Rank records (CUS-* codes).")

# 3. Also clear UNK- codes (auto-generated for unknown sea service ranks)
unk_ranks = Rank.objects.filter(code__startswith="UNK-")
unk_count = 0
for rank in unk_ranks:
    rank.code = f"CLR-{uuid.uuid4().hex[:8].upper()}"
    rank.save(update_fields=['code'])
    unk_count += 1
print(f"Cleared rank_code on {unk_count} Rank records (UNK-* codes).")

print(f"\nDone! Cleared {ur_count} assigned_codes, {cus_count + unk_count} rank_codes.")
