import requests

url = "http://localhost:8000/api/documents/"
files = {'file': ('test.pdf', b'%PDF-1.4\n%...', 'application/pdf')}
data = {
    'title': 'Test Document',
    'email': 'test_applicant@example.com',
    'name': 'Test Applicant'
}

response = requests.post(url, data=data, files=files)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
