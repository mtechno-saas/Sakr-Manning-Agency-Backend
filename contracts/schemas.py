from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import date

class Education(BaseModel):
    degree: str
    institution: str
    year: int

class TravelDocument(BaseModel):
    doc_type: str
    doc_number: str
    issue_date: date
    expiry_date: date
    issued_by: str

class ContractData(BaseModel):
    # Personal Details
    full_name: str
    date_of_birth: date
    marital_status: str
    nationality: str
    height_cm: float
    weight_kg: float
    place_of_birth: str
    shirt_size: str
    trouser_size: str
    shoe_size: str
    
    # Education
    education: Optional[str] = None
    english_fluency: str # Fluent, Good, Average, Poor
    
    # Contact
    address: str
    email: EmailStr
    phone_number: str
    
    # Travel Docs - we might need to map these to specific fields or just take list
    passport_number: Optional[str] = None
    passport_issue_date: Optional[date] = None
    passport_expiry_date: Optional[date] = None
    passport_issued_by: Optional[str] = None
    
    seaman_book_number: Optional[str] = None
    seaman_book_issue_date: Optional[date] = None
    seaman_book_expiry_date: Optional[date] = None
    seaman_book_issued_by: Optional[str] = None
    
    # Next of Kin
    next_of_kin_name: str
    next_of_kin_relationship: str
    next_of_kin_address: str
    next_of_kin_phone: str
