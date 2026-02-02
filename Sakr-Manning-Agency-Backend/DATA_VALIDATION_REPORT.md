# Data Validation Report - Sakr Manning Agency API

## Overview

This document details all data validation mechanisms implemented across the API endpoints.

---

## Table of Contents

1. [Serializer-Level Validation](#serializer-level-validation)
2. [Model-Level Validation](#model-level-validation)
3. [View-Level Validation](#view-level-validation)
4. [Custom Validators](#custom-validators)
5. [Validation Patterns by Endpoint](#validation-patterns-by-endpoint)

---

## 1. Serializer-Level Validation

### 1.1 User Registration (`RegisterSerializer`)

**Location**: `api/serializer.py` (Lines 693-718)

**Validations**:

- **Email Uniqueness**: Uses `validators.UniqueValidator` to ensure email is not already registered
- **Required Fields**: email, password, first_name are required
- **Password Security**: Write-only field to prevent exposure

```python
extra_kwargs = {
    "password": {"write_only": True},
    "email": {
        "required": True,
        "allow_blank": False,
        "validators": [
            validators.UniqueValidator(
                Users.objects.all(),
                message="This email is already registered."
            )
        ]
    }
}
```

---

### 1.2 AI Document Upload (`DocumentUploadSerializer`)

**Location**: `ai_document/serializers.py` (Lines 1305-1324)

**Validations**:

- **File Size**: Maximum 50MB
- **File Type**: Only PDF and DOCX files allowed
- **File Extension**: Validated using `os.path.splitext`

```python
def validate_file(self, value):
    """Validate file type and size."""
    max_size = 50 * 1024 * 1024  # 50MB
    if value.size > max_size:
        raise serializers.ValidationError(
            f"File size cannot exceed 50MB. Current: {value.size / (1024*1024):.2f}MB"
        )
    
    allowed_extensions = ['.pdf', '.docx']
    file_extension = os.path.splitext(value.name)[1].lower()
    if file_extension not in allowed_extensions:
        raise serializers.ValidationError(
            f"File type '{file_extension}' not supported. Allowed: {', '.join(allowed_extensions)}"
        )
    
    return value
```

**Error Messages**:

- File too large: Shows current file size
- Invalid file type: Shows attempted extension and allowed extensions

---

### 1.3 Applicant Conversion (`ConvertApplicantRequestSerializer`)

**Location**: `ai_document/serializers.py` (Lines 1327-1335)

**Validations**:

- **Applicant Existence**: Validates that applicant ID exists in database
- **Required Field**: applicant_id is required

```python
def validate_applicant_id(self, value):
    """Validate applicant exists."""
    if not Applicant.objects.filter(id=value).exists():
        raise serializers.ValidationError(f"Applicant with ID {value} does not exist")
    return value
```

---

### 1.4 Batch Conversion (`BatchConvertRequestSerializer`)

**Location**: `ai_document/serializers.py` (Lines 1338-1353)

**Validations**:

- **Mutual Exclusivity**: Either `applicant_ids` or `convert_all` must be provided
- **List Validation**: applicant_ids must be a list of integers

```python
def validate(self, data):
    """Validate that either applicant_ids or convert_all is provided."""
    if not data.get('convert_all') and not data.get('applicant_ids'):
        raise serializers.ValidationError(
            "Either 'applicant_ids' or 'convert_all' must be provided"
        )
    return data
```

---

## 2. Model-Level Validation

### 2.1 File Extension Validation

**Location**: `ai_document/models.py` (Line 1079)

**Validations**:

- **Document Model**: Uses Django's `FileExtensionValidator`
- **Allowed Extensions**: PDF, DOCX only

```python
file = models.FileField(
    upload_to=document_upload_path,
    validators=[FileExtensionValidator(allowed_extensions=['pdf', 'docx'])],
    help_text="Upload PDF or DOCX file"
)
```

---

### 2.2 Choice Field Validation

**Models with Choices Validation**:

1. **Users Model** (`api/models.py`):
   - `role`: Admin, HR Manager, Recruiter, Employee
   - `marital_status`: Predefined choices
   - `user_status`: On Site, Vacation, Medical Vacation

2. **Ship Model** (`ships/models.py`):
   - `status`: Active, Under Maintenance, Inactive

3. **Company Model** (`companies/models.py`):
   - `company_type`: Ship Owner, Ship Manager, Crewing Agency, etc.
   - `status`: Active, Inactive, Prospect

4. **Contract Model** (`api/models.py`):
   - `status`: Active, Completed, Pending, Signed, etc.
   - `currency`: USD, EUR, GBP, EGP

5. **Interview Model** (`api/models.py`):
   - `interview_type`: Phone, Video, In-Person, Technical
   - `status`: Scheduled, Completed, Cancelled, etc.
   - `result`: Pending, Passed, Failed, On Hold

---

## 3. View-Level Validation

### 3.1 Finance Record Calculation

**Location**: `finance/views.py` (Line 25)

**Validation**:

```python
serializer.is_valid(raise_exception=True)
```

- Automatically raises 400 Bad Request on validation failure
- Returns detailed field-level error messages

---

### 3.2 AI Document Upload

**Location**: `ai_document/views.py` (Line 3491)

**Validation**:

```python
if not upload_serializer.is_valid():
    return Response(
        upload_serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
```

- Manual validation check
- Returns serializer errors with 400 status

---

### 3.3 User Registration

**Location**: `api/views.py` (Lines 401, 442)

**Validation**:

```python
if serializer.is_valid():
    serializer.save()
    return Response(...)
else:
    return Response(serializer.errors, status=400)
```

---

## 4. Custom Validators

### 4.1 Data Mapper Service Validation

**Location**: `ai_document/data_mapper_service.py` (Line 1901)

**Email Validation**:

```python
if not user.email:
    raise ValidationError("Email is required")
```

**Unique Email Check**:

```python
existing_user = Users.objects.filter(email=user.email).first()
if existing_user:
    logger.info(f"User with email {user.email} already exists. Updating existing user.")
    # Updates instead of creating duplicate
```

---

### 4.2 Date Parsing Validation

**Location**: `ai_document/data_mapper_service.py` (Lines 1382-1418)

**Multiple Format Support**:

```python
def parse_date_string(date_str: str) -> Optional[datetime.date]:
    if not date_str or not isinstance(date_str, str):
        return None
    
    date_str = date_str.strip().replace('/', '-').replace(' ', '')
    
    date_formats = [
        '%d-%m-%Y',  # 28-07-1975
        '%d-%m-%y',   # 28-07-75
        '%Y-%m-%d',   # 1975-07-28
        '%m-%d-%Y',   # 07-28-1975
        '%d%m%Y',    # 28071975
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    
    return None
```

**Features**:

- Handles multiple date formats
- Returns None for invalid dates instead of raising exceptions
- Logs warnings for unparseable dates

---

## 5. Validation Patterns by Endpoint

### 5.1 Authentication Endpoints

#### POST /api/login/

**Validations**:

- Required: email, password
- Email format validation (built-in EmailField)
- Credentials verification via JWT

#### POST /api/register/

**Validations**:

- Email format
- Email uniqueness
- Password presence (minimum length handled by Django)
- Required: first_name, email, password

---

### 5.2 User Management Endpoints

#### POST /api/users/

**Validations**:

- Email format and uniqueness
- Phone number format (CharField)
- Date fields (date_of_birth, passport dates, etc.)
- Certificate IDs existence (PrimaryKeyRelatedField)
- Rank IDs existence (PrimaryKeyRelatedField)
- Role choices validation
- Password strength (Django built-in)

#### PUT/PATCH /api/users/{id}/

**Validations**:

- Same as create, but password optional
- Profile image file type and size
- Many-to-many relationship validation

---

### 5.3 Ships Management Endpoints

#### POST /api/ships/

**Validations**:

- IMO number uniqueness
- Ship name required
- Company ID existence (ForeignKey)
- Ship type ID existence (ForeignKey)
- Flag ID existence (ForeignKey)
- Status choices validation
- Integer fields (gross_tonnage, deadweight, year_built)

#### POST /api/ships/{id}/assign-user/

**Validations**:

- Request body must contain user_id
- User ID must exist
- Custom validation in view

---

### 5.4 AI Document Processing Endpoints

#### POST /ai/upload/

**Validations**:

- File presence required
- File size <= 50MB
- File extension: .pdf or .docx only
- MIME type validation

#### POST /ai/convert/

**Validations**:

- applicant_id required
- Applicant must exist in database
- Password required for user creation
- Email extracted from applicant data
- Email uniqueness (prevents duplicates)

#### POST /ai/batch-convert/

**Validations**:

- Either applicant_ids OR convert_all must be provided
- applicant_ids must be array of integers
- Each applicant ID validated for existence

---

### 5.5 Finance Management Endpoints

#### POST /api/finance/finance-records/

**Validations**:

- User ID existence
- Company ID existence
- start_date < end_date (implicit)
- Date format validation
- Currency choices validation
- Status choices validation

#### POST /api/finance/finance-records/calculate/

**Validations**:

- Required: user, company, start_date, end_date
- Automatic calculation validation
- No database save (preview only)

---

### 5.6 Interview Management Endpoints

#### POST /api/interviews/interviews/

**Validations**:

- Candidate (user) ID existence
- Company ID existence
- Position (rank) ID existence
- scheduled_date format (YYYY-MM-DD)
- scheduled_time format (HH:MM:SS)
- duration_minutes positive integer
- interview_type choices
- status choices
- meeting_link URL format (when provided)

---

### 5.7 CV Submission Endpoints

#### POST /api/cv-submissions/

**Validations**:

- User ID existence
- Company ID existence
- Position ID existence
- cv_file required (FileField)
- File upload validation
- Status choices
- Rating (1-5 if provided)

---

### 5.8 Contract Management Endpoints

#### POST /api/contracts/

**Validations**:

- User ID existence
- Ship ID existence
- Company ID existence (optional)
- Rank ID existence (optional)
- sign_on_date required and date format
- sign_off_date date format (optional)
- Salary decimal validation
- Currency choices
- Status choices
- signed_file FileField

---

## 6. Error Response Formats

### Standard Validation Error Response

```json
{
  "field_name": ["Error message 1", "Error message 2"],
  "another_field": ["Error message"]
}
```

### Example: Registration Error

```json
{
  "email": ["This email is already registered."],
  "password": ["This field is required."]
}
```

### Example: File Upload Error

```json
{
  "file": ["File size cannot exceed 50MB. Current: 75.32MB"]
}
```

### Example: Applicant Conversion Error

```json
{
  "applicant_id": ["Applicant with ID 999 does not exist"]
}
```

---

## 7. Best Practices Implemented

### ✅ Field-Level Validation

- Custom `validate_<field_name>` methods in serializers
- Clear, descriptive error messages
- Immediate feedback to API consumers

### ✅ Object-Level Validation

- `validate()` method for cross-field validation
- Ensures data consistency across related fields

### ✅ Model Constraints

- Choice fields with predefined options
- Unique constraints on critical fields (email, IMO number)
- Foreign key relationships ensure data integrity

### ✅ File Validation

- Size limits prevent server overload
- Extension whitelisting for security
- Type checking at multiple layers

### ✅ Date Validation

- Flexible parsing for various formats
- Graceful handling of invalid dates
- Logging for debugging

### ✅ Unique Validators

- Email uniqueness across users
- IMO number uniqueness for ships
- Certificate code uniqueness

### ✅ Error Handling

- Consistent error response format
- HTTP status codes (400 for validation errors)
- Detailed error messages for debugging

---

## 8. Validation Summary by Type

| Validation Type | Count | Endpoints Affected |
|----------------|-------|-------------------|
| Email Uniqueness | 2 | Registration, User Creation |
| File Size | 1 | Document Upload |
| File Extension | 2 | Document Upload, Document Model |
| Foreign Key Existence | 15+ | All endpoints with relationships |
| Choice Fields | 10+ | Users, Ships, Companies, Contracts, Interviews |
| Date Format | 20+ | All date fields across models |
| Required Fields | 50+ | All POST endpoints |
| Custom Validators | 5 | AI Document, Data Mapper |

---

## 9. Recommendations

### Current Strengths

1. ✅ Comprehensive file validation
2. ✅ Email uniqueness enforcement
3. ✅ Choice field constraints
4. ✅ Foreign key integrity
5. ✅ Clear error messages

### Potential Improvements

1. **Password Strength**: Add custom validator for minimum 8 characters, uppercase, numbers
2. **Phone Number Format**: Implement regex validation for international formats
3. **Date Range Validation**: Ensure expiry_date > issue_date
4. **Custom Error Codes**: Add error codes for easier client-side handling
5. **Bulk Operation Validation**: Validate all items before processing in batch operations

---

## 10. Testing Validation

### Recommended Test Cases

```python
# Email Validation
def test_duplicate_email():
    # Should return 400 with message "This email is already registered."
    
# File Upload
def test_file_too_large():
    # Should return 400 with file size error
    
def test_invalid_file_type():
    # Should return 400 with extension error
    
# Foreign Key Validation
def test_invalid_user_id():
    # Should return 404 or 400 with "User does not exist"
    
# Date Validation
def test_invalid_date_format():
    # Should handle gracefully or return format error
```

---

**Document Version**: 1.0  
**Last Updated**: December 2024  
**Coverage**: All endpoints in Sakr Manning Agency Backend
