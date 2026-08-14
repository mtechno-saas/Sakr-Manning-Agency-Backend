import django
django.setup()
from companies.models import Company
c = Company.objects.filter(company_name__icontains='3 seas shipping').first()
if c:
    print('company =', repr(c.company_name))
    print('website raw =', repr(c.website))
    print('len of website =', len(c.website) if c.website else 0)
    if c.website:
        print('starts with https?', c.website.startswith('https'))
        print('starts with http?', c.website.startswith('http'))
else:
    print('Company not found locally')
