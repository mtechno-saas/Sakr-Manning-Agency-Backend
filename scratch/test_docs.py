import sys, django, os
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'saker.settings')
django.setup()

from api.models import Users
from api.serializer import UsersSerializer

user = Users.objects.first()
user_data = UsersSerializer(user).data
docs = user_data.get('user_documents', [])
print(type(docs), len(docs))
if docs:
    print(type(docs[0]), docs[0])
