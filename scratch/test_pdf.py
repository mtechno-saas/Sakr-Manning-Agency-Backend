import sys, django, os
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from api.models import Users
from api.serializer import UsersSerializer, ContractListSerializer
from api.models import Contract
from api.pdf_generator import generate_full_profile_pdf

user = Users.objects.first()
user_data = UsersSerializer(user).data
contracts = Contract.objects.filter(user=user).select_related('ship', 'company', 'rank')
user_data['contracts'] = ContractListSerializer(contracts, many=True).data

pdf_bytes = generate_full_profile_pdf(user_data, logo_path=None)
print("PDF generated successfully. Size:", len(pdf_bytes))
