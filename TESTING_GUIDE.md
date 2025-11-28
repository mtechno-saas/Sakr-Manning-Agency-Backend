# Quick Start Guide - Testing Create User Endpoint

## Step 1: Start the Django Development Server

Open a terminal and run:

```bash
cd "/run/media/storm/TECNO SQUEARE/django test"
python manage.py runserver
```

You should see output like:

```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## Step 2: Run the Test Script

Open a **new terminal** (keep the server running in the first one) and run:

```bash
cd "/run/media/storm/TECNO SQUEARE/django test"
python test_create_user.py
```

## Alternative: Test with curl

If you prefer to test manually with curl:

```bash
curl -X POST http://localhost:8000/api/users/create/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "captain@example.com",
    "password": "SecurePassword123!",
    "first_name": "James",
    "middle_name": "Robert",
    "phone_number": "+1234567890",
    "nationality": "Egypt",
    "date_of_birth": "1985-05-15",
    "role": "Employee"
  }'
```

## Alternative: Test with Python requests

Create a simple test:

```python
import requests
import json

response = requests.post(
    "http://localhost:8000/api/users/create/",
    json={
        "email": "captain@example.com",
        "password": "SecurePassword123!",
        "first_name": "James",
        "middle_name": "Robert",
        "phone_number": "+1234567890",
        "nationality": "Egypt",
        "date_of_birth": "1985-05-15",
        "role": "Employee"
    }
)

print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))
```

## Troubleshooting

### If you get "connection refused" error

- Make sure the Django server is running (`python manage.py runserver`)
- Check that it's running on port 8000
- Try accessing <http://localhost:8000/admin/> in your browser to verify

### If you get authentication errors

- The endpoint may require authentication
- Check your Django REST Framework settings in settings.py
- You may need to add authentication headers or temporarily allow unauthenticated access

### If you get validation errors

- Check that `email`, `first_name`, and `phone_number` are provided
- Make sure `rank_ids` and `certificate_ids` reference existing database entries
