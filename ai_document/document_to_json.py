# import json
# import re
# from langchain.prompts import PromptTemplate
# from langchain.output_parsers import StructuredOutputParser, ResponseSchema
# from langchain_ollama import OllamaLLM

# # 1. Define schema fields
# response_schemas = [
#     ResponseSchema(name="Personal_Details", description="Personal details of the applicant"),
#     ResponseSchema(name="Education", description="Education and language skills"),
#     ResponseSchema(name="Contact_Details", description="Contact information"),
#     ResponseSchema(name="Travel_Documents", description="Passport, seaman book, etc."),
#     ResponseSchema(name="Professional_Qualifications", description="Certificates of competency and qualifications"),
#     ResponseSchema(name="Next_of_Kin_Emergency_Contact", description="Next of kin or emergency contacts"),
#     ResponseSchema(name="Health_Certificates_Vaccinations", description="Health certificates and vaccinations"),
#     ResponseSchema(name="Covid_19_Vaccination", description="Covid-19 vaccination details"),
#     ResponseSchema(name="Marine_Courses", description="Marine and safety training courses"),
#     ResponseSchema(name="Sea_Service_Details", description="Details of sea service records"),
#     ResponseSchema(name="Specialised_Experience", description="Specialised experiences if any"),
#     ResponseSchema(name="References", description="References provided by the applicant"),
#     ResponseSchema(name="Declaration", description="Declaration, health questions, signature, date"),
#     ResponseSchema(name="Office_Use_Only", description="Office assessment and signature"),
# ]

# # 2. Create the parser
# output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# # 3. Format instructions (JSON schema instructions)
# format_instructions = output_parser.get_format_instructions()


# def repair_json_string(text: str) -> str:
#     """Fix common JSON formatting errors from LLM output."""
    
#     if hasattr(text, 'content'):
#         text = text.content
#     else:
#         text = str(text)
    
#     # Remove markdown code fences
#     text = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE)
    
#     # Remove any control characters that cause parsing issues
#     text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
#     # Fix broken syntax - ensure proper JSON structure
#     # Remove any trailing incomplete parts
#     brace_count = 0
#     last_complete_pos = 0
    
#     for i, char in enumerate(text):
#         if char == '{':
#             brace_count += 1
#         elif char == '}':
#             brace_count -= 1
#             if brace_count == 0:
#                 last_complete_pos = i + 1
    
#     # Truncate to last complete JSON object
#     if last_complete_pos > 0:
#         text = text[:last_complete_pos]
    
#     # Fix trailing commas
#     text = re.sub(r',\s*}', '}', text)
#     text = re.sub(r',\s*]', ']', text)
    
#     # Fix multiple commas
#     text = re.sub(r',\s*,+', ',', text)
    
#     return text


# def extract_json_data_manually(text: str) -> dict:
#     """Manually extract data from malformed JSON when parsing fails."""
#     result = {}
    
#     # Define the expected keys
#     expected_keys = [
#         "Personal_Details", "Education", "Contact_Details", "Travel_Documents",
#         "Professional_Qualifications", "Next_of_Kin_Emergency_Contact",
#         "Health_Certificates_Vaccinations", "Covid_19_Vaccination", "Marine_Courses",
#         "Sea_Service_Details", "Specialised_Experience", "References",
#         "Declaration", "Office_Use_Only"
#     ]
    
#     for key in expected_keys:
#         result[key] = {}
    
#     # Extract personal details
#     name_match = re.search(r'"name":\s*"([^"]*)"', text, re.IGNORECASE)
#     if name_match:
#         result["Personal_Details"]["name"] = name_match.group(1)
    
#     email_match = re.search(r'"email":\s*"([^"]*@[^"]*)"', text, re.IGNORECASE)
#     if email_match:
#         result["Personal_Details"]["email"] = email_match.group(1)
#         result["Contact_Details"]["email"] = email_match.group(1)
    
#     phone_match = re.search(r'"phone":\s*"([^"]*)"', text, re.IGNORECASE)
#     if phone_match:
#         result["Personal_Details"]["phone"] = phone_match.group(1)
#         result["Contact_Details"]["phone"] = phone_match.group(1)
    
#     nationality_match = re.search(r'"nationality":\s*"([^"]*)"', text, re.IGNORECASE)
#     if nationality_match:
#         result["Personal_Details"]["nationality"] = nationality_match.group(1)
    
#     birth_date_match = re.search(r'"birth_date":\s*"([^"]*)"', text, re.IGNORECASE)
#     if birth_date_match:
#         result["Personal_Details"]["birth_date"] = birth_date_match.group(1)
    
#     address_match = re.search(r'"address":\s*"([^"]*)"', text, re.IGNORECASE)
#     if address_match:
#         result["Personal_Details"]["address"] = address_match.group(1)
#         result["Contact_Details"]["address"] = address_match.group(1)
    
#     return result


# def convert_text_to_json(extracted_text: str) -> dict:
#     """
#     Convert extracted document text into structured JSON using Ollama.
#     Returns a dictionary, not a string.
#     """
#     llm = OllamaLLM(model="llama3.2:1b", temperature=0)

#     # Truncate text if too long
#     max_chars = 3000
#     truncated_text = extracted_text[:max_chars] if len(extracted_text) > max_chars else extracted_text

#     prompt = PromptTemplate(
#         template="""You are a JSON generator. Extract information from this CV text and return ONLY valid JSON.

# CV Text:
# {document}

# Return a JSON object with these keys (use empty object {{}} if no data found):
# - Personal_Details (name, birth_date, nationality, address, email, phone)
# - Education (schools, languages)
# - Contact_Details (email, phone, address)
# - Travel_Documents (passport details)
# - Professional_Qualifications (certificates)
# - Sea_Service_Details (ship experience)
# - Marine_Courses (training)

# CRITICAL RULES:
# 1. Return ONLY the JSON object, no explanations
# 2. Use double quotes for all strings
# 3. Do NOT escape quotes inside values
# 4. Do NOT use parentheses in JSON
# 5. Use simple strings, not nested quotes

# Example format:
# {{
#   "Personal_Details": {{
#     "name": "John Doe",
#     "birth_date": "01/01/1990"
#   }},
#   "Education": {{}}
# }}
# """,
#         input_variables=["document"],
#     )

#     chain = prompt | llm
#     raw_result = chain.invoke({"document": truncated_text})
    
#     print("=" * 80)
#     print("RAW LLM OUTPUT:")
#     print(raw_result)
#     print("=" * 80)
    
#     # Handle the case where raw_result might already be a dict
#     if isinstance(raw_result, dict):
#         print("LLM returned a dictionary directly")
#         result = raw_result
#     else:
#         # More aggressive cleaning
#         try:
#             # Extract just the JSON part if there's extra text
#             json_match = re.search(r'\{.*\}', str(raw_result), re.DOTALL)
#             if json_match:
#                 raw_result = json_match.group(0)
            
#             cleaned = repair_json_string(str(raw_result))
#             print(f"Cleaned JSON length: {len(cleaned)}")
#             print(f"Cleaned text preview: {cleaned[:200]}...")
            
#             result = json.loads(cleaned)
#             print("Successfully parsed JSON")
            
#         except Exception as e:
#             print(f"Parsing failed: {e}")
#             print(f"Attempting manual extraction...")
            
#             # Try manual extraction as fallback
#             try:
#                 result = extract_json_data_manually(str(raw_result))
#                 print("Manual extraction successful")
#             except Exception as manual_error:
#                 print(f"Manual extraction also failed: {manual_error}")
#                 result = {
#                     "Personal_Details": {},
#                     "Education": {},
#                     "Contact_Details": {},
#                     "Travel_Documents": {},
#                     "Professional_Qualifications": {},
#                     "Next_of_Kin_Emergency_Contact": {},
#                     "Health_Certificates_Vaccinations": {},
#                     "Covid_19_Vaccination": {},
#                     "Marine_Courses": {},
#                     "Sea_Service_Details": {},
#                     "Specialised_Experience": {},
#                     "References": {},
#                     "Declaration": {},
#                     "Office_Use_Only": {},
#                     "error": str(e),
#                     "raw_output": str(raw_result)[:500]
#                 }
    
#     # Ensure all expected keys exist
#     expected_keys = [
#         "Personal_Details", "Education", "Contact_Details", "Travel_Documents",
#         "Professional_Qualifications", "Next_of_Kin_Emergency_Contact",
#         "Health_Certificates_Vaccinations", "Covid_19_Vaccination", "Marine_Courses",
#         "Sea_Service_Details", "Specialised_Experience", "References",
#         "Declaration", "Office_Use_Only"
#     ]
    
#     for key in expected_keys:
#         if key not in result:
#             result[key] = {}
    
#     print(f"Final result type: {type(result)}")
#     print(f"Final result keys: {list(result.keys())}")
    
#     return result


# # Alternative function with more aggressive JSON cleaning
# def convert_text_to_json_robust(extracted_text: str) -> dict:
#     """
#     More robust version with additional JSON repair strategies.
#     Always returns a dictionary.
#     """
    
#     llm = OllamaLLM(model="llama3.2:1b")

#     prompt = PromptTemplate(
#         template="""
# You are an expert information extraction system.

# Extract structured data from the following CV text and return it as valid JSON.

# Text:
# {document}

# CRITICAL: Return ONLY a valid JSON object. No explanations, no markdown, no extra text.

# Extract information for these categories:
# - Personal_Details: Full name, nationality, date of birth, etc.
# - Education: Educational background and language skills
# - Contact_Details: Address, phone, email
# - Travel_Documents: Passport details, seaman's book
# - Professional_Qualifications: Certificates and licenses
# - Next_of_Kin_Emergency_Contact: Emergency contact information
# - Health_Certificates_Vaccinations: Health and vaccination records
# - Covid_19_Vaccination: COVID vaccination details
# - Marine_Courses: Maritime training and courses
# - Sea_Service_Details: Previous sea service experience
# - Specialised_Experience: Any specialized skills or experience
# - References: Professional references
# - Declaration: Declarations and signatures
# - Office_Use_Only: Internal office notes

# Use empty strings "" for missing information.
# """,
#         input_variables=["document"],
#     )

#     chain = prompt | llm
#     raw_result = chain.invoke({"document": extracted_text})
    
#     # Handle different result types
#     if isinstance(raw_result, dict):
#         return raw_result
    
#     # Multiple parsing attempts
#     parsing_attempts = [
#         lambda x: json.loads(str(x)),
#         lambda x: json.loads(repair_json_string(str(x))),
#         lambda x: extract_json_data_manually(str(x)),
#     ]
    
#     for attempt in parsing_attempts:
#         try:
#             result = attempt(raw_result)
#             if isinstance(result, dict):
#                 return result
#         except Exception:
#             continue
    
#     # Final fallback - always return a dict
#     return {
#         "Personal_Details": {},
#         "Education": {},
#         "Contact_Details": {},
#         "Travel_Documents": {},
#         "Professional_Qualifications": {},
#         "Next_of_Kin_Emergency_Contact": {},
#         "Health_Certificates_Vaccinations": {},
#         "Covid_19_Vaccination": {},
#         "Marine_Courses": {},
#         "Sea_Service_Details": {},
#         "Specialised_Experience": {},
#         "References": {},
#         "Declaration": {},
#         "Office_Use_Only": {},
#         "error": "All parsing methods failed", 
#         "raw_output": str(raw_result)[:500]
#     }


















# import json
# import re
# from langchain.prompts import PromptTemplate
# from langchain.output_parsers import StructuredOutputParser, ResponseSchema
# from langchain_ollama import OllamaLLM

# # 1. Define schema fields - UPDATED WITH NEW CATEGORIES
# response_schemas = [
#     ResponseSchema(name="Personal_Details", description="Personal details of the applicant"),
#     ResponseSchema(name="Education", description="Education and language skills"),
#     ResponseSchema(name="Contact_Details", description="Contact information"),
#     ResponseSchema(name="Travel_Documents", description="Passport, seaman book, etc."),
#     ResponseSchema(name="Professional_Qualifications", description="Certificates of competency and qualifications"),
#     ResponseSchema(name="Next_of_Kin_Emergency_Contact", description="Next of kin or emergency contacts"),
#     ResponseSchema(name="Health_Certificates_Vaccinations", description="Health certificates and vaccinations"),
#     ResponseSchema(name="Covid_19_Vaccination", description="Covid-19 vaccination details"),
#     ResponseSchema(name="Marine_Courses", description="Marine and safety training courses"),
#     ResponseSchema(name="Sea_Service_Details", description="Details of sea service records"),
#     ResponseSchema(name="Specialised_Experience", description="Specialised experiences if any"),
#     ResponseSchema(name="References", description="References provided by the applicant"),
#     ResponseSchema(name="Declaration", description="Declaration, health questions, signature, date"),
#     ResponseSchema(name="Office_Use_Only", description="Office assessment and signature"),
#     # NEW CATEGORIES ADDED
#     ResponseSchema(name="Physical_Measurements", description="Physical measurements like overall size, shirt size, trouser size, shoes size"),
#     ResponseSchema(name="Language_Skills", description="Language proficiency including English level and other languages"),
#     ResponseSchema(name="Medical_History", description="Medical history including disease history, accident history, psychiatric treatment, addiction history"),
#     ResponseSchema(name="Assessments", description="Various assessments and test results including Marlins test"),
#     ResponseSchema(name="Competency_Tests", description="Competency test results and certifications"),
# ]

# # 2. Create the parser
# output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# # 3. Format instructions (JSON schema instructions)
# format_instructions = output_parser.get_format_instructions()


# def repair_json_string(text: str) -> str:
#     """Fix common JSON formatting errors from LLM output."""
    
#     if hasattr(text, 'content'):
#         text = text.content
#     else:
#         text = str(text)
    
#     # Remove markdown code fences
#     text = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE)
    
#     # Remove any control characters that cause parsing issues
#     text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
#     # Fix broken syntax - ensure proper JSON structure
#     # Remove any trailing incomplete parts
#     brace_count = 0
#     last_complete_pos = 0
    
#     for i, char in enumerate(text):
#         if char == '{':
#             brace_count += 1
#         elif char == '}':
#             brace_count -= 1
#             if brace_count == 0:
#                 last_complete_pos = i + 1
    
#     # Truncate to last complete JSON object
#     if last_complete_pos > 0:
#         text = text[:last_complete_pos]
    
#     # Fix trailing commas
#     text = re.sub(r',\s*}', '}', text)
#     text = re.sub(r',\s*]', ']', text)
    
#     # Fix multiple commas
#     text = re.sub(r',\s*,+', ',', text)
    
#     return text


# def extract_json_data_manually(text: str) -> dict:
#     """Manually extract data from malformed JSON when parsing fails."""
#     result = {}
    
#     # Define the expected keys - UPDATED WITH NEW CATEGORIES
#     expected_keys = [
#         "Personal_Details", "Education", "Contact_Details", "Travel_Documents",
#         "Professional_Qualifications", "Next_of_Kin_Emergency_Contact",
#         "Health_Certificates_Vaccinations", "Covid_19_Vaccination", "Marine_Courses",
#         "Sea_Service_Details", "Specialised_Experience", "References",
#         "Declaration", "Office_Use_Only",
#         # NEW CATEGORIES
#         "Physical_Measurements", "Language_Skills", "Medical_History", 
#         "Assessments", "Competency_Tests"
#     ]
    
#     for key in expected_keys:
#         result[key] = {}
    
#     # Extract personal details
#     name_match = re.search(r'"name":\s*"([^"]*)"', text, re.IGNORECASE)
#     if name_match:
#         result["Personal_Details"]["name"] = name_match.group(1)
    
#     email_match = re.search(r'"email":\s*"([^"]*@[^"]*)"', text, re.IGNORECASE)
#     if email_match:
#         result["Personal_Details"]["email"] = email_match.group(1)
#         result["Contact_Details"]["email"] = email_match.group(1)
    
#     phone_match = re.search(r'"phone":\s*"([^"]*)"', text, re.IGNORECASE)
#     if phone_match:
#         result["Personal_Details"]["phone"] = phone_match.group(1)
#         result["Contact_Details"]["phone"] = phone_match.group(1)
    
#     nationality_match = re.search(r'"nationality":\s*"([^"]*)"', text, re.IGNORECASE)
#     if nationality_match:
#         result["Personal_Details"]["nationality"] = nationality_match.group(1)
    
#     birth_date_match = re.search(r'"birth_date":\s*"([^"]*)"', text, re.IGNORECASE)
#     if birth_date_match:
#         result["Personal_Details"]["birth_date"] = birth_date_match.group(1)
    
#     address_match = re.search(r'"address":\s*"([^"]*)"', text, re.IGNORECASE)
#     if address_match:
#         result["Personal_Details"]["address"] = address_match.group(1)
#         result["Contact_Details"]["address"] = address_match.group(1)
    
#     # Extract physical measurements
#     overall_size_match = re.search(r'"overall[_\s]*size":\s*"([^"]*)"', text, re.IGNORECASE)
#     if overall_size_match:
#         result["Physical_Measurements"]["overall_size"] = overall_size_match.group(1)
    
#     shirt_size_match = re.search(r'"shirt[_\s]*size":\s*"([^"]*)"', text, re.IGNORECASE)
#     if shirt_size_match:
#         result["Physical_Measurements"]["shirt_size"] = shirt_size_match.group(1)
    
#     # Extract language skills
#     english_match = re.search(r'"english[_\s]*level":\s*"([^"]*)"', text, re.IGNORECASE)
#     if english_match:
#         result["Language_Skills"]["english_language_level"] = english_match.group(1)
    
#     # Extract Marlins test data
#     marlins_match = re.search(r'"marlins[_\s]*test[_\s]*result":\s*"([^"]*)"', text, re.IGNORECASE)
#     if marlins_match:
#         result["Assessments"]["marlins_test_result"] = marlins_match.group(1)
    
#     return result


# def convert_text_to_json(extracted_text: str) -> dict:
#     """
#     Convert extracted document text into structured JSON using Ollama.
#     Returns a dictionary, not a string.
#     """
#     llm = OllamaLLM(model="llama3.2:1b", temperature=0)

#     # Truncate text if too long
#     max_chars = 3000
#     truncated_text = extracted_text[:max_chars] if len(extracted_text) > max_chars else extracted_text

#     prompt = PromptTemplate(
#         template="""You are a JSON generator. Extract information from this CV text and return ONLY valid JSON.

# CV Text:
# {document}

# Return a JSON object with these keys (use empty object {{}} if no data found):
# - Personal_Details (name, birth_date, nationality, address, email, phone)
# - Education (schools, languages)
# - Contact_Details (email, phone, address)
# - Travel_Documents (passport details, seaman book)
# - Professional_Qualifications (certificates)
# - Sea_Service_Details (ship experience)
# - Marine_Courses (training)
# - Physical_Measurements (overall_size, shirt_size, trouser_size, shoes_size)
# - Language_Skills (english_language_level, other_language, other_language_level)
# - Medical_History (disease_history, accident_history, psychiatric_treatment_history, addiction_history)
# - Assessments (marlins_test_result, marlins_test_issued_date, marlins_test_issued_at, marlins_test_issued_by)
# - Competency_Tests (test results and certifications)

# CRITICAL RULES:
# 1. Return ONLY the JSON object, no explanations
# 2. Use double quotes for all strings
# 3. Do NOT escape quotes inside values
# 4. Do NOT use parentheses in JSON
# 5. Use simple strings, not nested quotes
# 6. Extract size information (L, M, XL, 42, etc.) to Physical_Measurements
# 7. Extract language proficiency to Language_Skills
# 8. Extract medical history to Medical_History
# 9. Extract test results to Assessments and Competency_Tests

# Example format:
# {{
#   "Personal_Details": {{
#     "name": "John Doe",
#     "birth_date": "01/01/1990"
#   }},
#   "Physical_Measurements": {{
#     "overall_size": "L",
#     "shirt_size": "M"
#   }},
#   "Language_Skills": {{
#     "english_language_level": "Good"
#   }},
#   "Education": {{}}
# }}
# """,
#         input_variables=["document"],
#     )

#     chain = prompt | llm
#     raw_result = chain.invoke({"document": truncated_text})
    
#     print("=" * 80)
#     print("RAW LLM OUTPUT:")
#     print(raw_result)
#     print("=" * 80)
    
#     # Handle the case where raw_result might already be a dict
#     if isinstance(raw_result, dict):
#         print("LLM returned a dictionary directly")
#         result = raw_result
#     else:
#         # More aggressive cleaning
#         try:
#             # Extract just the JSON part if there's extra text
#             json_match = re.search(r'\{.*\}', str(raw_result), re.DOTALL)
#             if json_match:
#                 raw_result = json_match.group(0)
            
#             cleaned = repair_json_string(str(raw_result))
#             print(f"Cleaned JSON length: {len(cleaned)}")
#             print(f"Cleaned text preview: {cleaned[:200]}...")
            
#             result = json.loads(cleaned)
#             print("Successfully parsed JSON")
            
#         except Exception as e:
#             print(f"Parsing failed: {e}")
#             print(f"Attempting manual extraction...")
            
#             # Try manual extraction as fallback
#             try:
#                 result = extract_json_data_manually(str(raw_result))
#                 print("Manual extraction successful")
#             except Exception as manual_error:
#                 print(f"Manual extraction also failed: {manual_error}")
#                 result = {
#                     "Personal_Details": {},
#                     "Education": {},
#                     "Contact_Details": {},
#                     "Travel_Documents": {},
#                     "Professional_Qualifications": {},
#                     "Next_of_Kin_Emergency_Contact": {},
#                     "Health_Certificates_Vaccinations": {},
#                     "Covid_19_Vaccination": {},
#                     "Marine_Courses": {},
#                     "Sea_Service_Details": {},
#                     "Specialised_Experience": {},
#                     "References": {},
#                     "Declaration": {},
#                     "Office_Use_Only": {},
#                     # NEW CATEGORIES
#                     "Physical_Measurements": {},
#                     "Language_Skills": {},
#                     "Medical_History": {},
#                     "Assessments": {},
#                     "Competency_Tests": {},
#                     "error": str(e),
#                     "raw_output": str(raw_result)[:500]
#                 }
    
#     # Ensure all expected keys exist - UPDATED WITH NEW CATEGORIES
#     expected_keys = [
#         "Personal_Details", "Education", "Contact_Details", "Travel_Documents",
#         "Professional_Qualifications", "Next_of_Kin_Emergency_Contact",
#         "Health_Certificates_Vaccinations", "Covid_19_Vaccination", "Marine_Courses",
#         "Sea_Service_Details", "Specialised_Experience", "References",
#         "Declaration", "Office_Use_Only",
#         # NEW CATEGORIES
#         "Physical_Measurements", "Language_Skills", "Medical_History", 
#         "Assessments", "Competency_Tests"
#     ]
    
#     for key in expected_keys:
#         if key not in result:
#             result[key] = {}
    
#     print(f"Final result type: {type(result)}")
#     print(f"Final result keys: {list(result.keys())}")
    
#     return result


# # Alternative function with more aggressive JSON cleaning
# def convert_text_to_json_robust(extracted_text: str) -> dict:
#     """
#     More robust version with additional JSON repair strategies.
#     Always returns a dictionary.
#     """
    
#     llm = OllamaLLM(model="llama3.2:1b")

#     prompt = PromptTemplate(
#         template="""
# You are an expert information extraction system.

# Extract structured data from the following CV text and return it as valid JSON.

# Text:
# {document}

# CRITICAL: Return ONLY a valid JSON object. No explanations, no markdown, no extra text.

# Extract information for these categories:
# - Personal_Details: Full name, nationality, date of birth, etc.
# - Education: Educational background and language skills
# - Contact_Details: Address, phone, email
# - Travel_Documents: Passport details, seaman's book
# - Professional_Qualifications: Certificates and licenses
# - Next_of_Kin_Emergency_Contact: Emergency contact information
# - Health_Certificates_Vaccinations: Health and vaccination records
# - Covid_19_Vaccination: COVID vaccination details
# - Marine_Courses: Maritime training and courses
# - Sea_Service_Details: Previous sea service experience
# - Specialised_Experience: Any specialized skills or experience
# - References: Professional references
# - Declaration: Declarations and signatures
# - Office_Use_Only: Internal office notes
# - Physical_Measurements: Overall size, shirt size, trouser size, shoes size
# - Language_Skills: English proficiency level, other languages
# - Medical_History: Disease history, accident history, psychiatric treatment, addiction history
# - Assessments: Marlins test results and other assessments
# - Competency_Tests: Various competency test results

# Use empty strings "" for missing information.
# """,
#         input_variables=["document"],
#     )

#     chain = prompt | llm
#     raw_result = chain.invoke({"document": extracted_text})
    
#     # Handle different result types
#     if isinstance(raw_result, dict):
#         return raw_result
    
#     # Multiple parsing attempts
#     parsing_attempts = [
#         lambda x: json.loads(str(x)),
#         lambda x: json.loads(repair_json_string(str(x))),
#         lambda x: extract_json_data_manually(str(x)),
#     ]
    
#     for attempt in parsing_attempts:
#         try:
#             result = attempt(raw_result)
#             if isinstance(result, dict):
#                 return result
#         except Exception:
#             continue
    
#     # Final fallback - always return a dict - UPDATED WITH NEW CATEGORIES
#     return {
#         "Personal_Details": {},
#         "Education": {},
#         "Contact_Details": {},
#         "Travel_Documents": {},
#         "Professional_Qualifications": {},
#         "Next_of_Kin_Emergency_Contact": {},
#         "Health_Certificates_Vaccinations": {},
#         "Covid_19_Vaccination": {},
#         "Marine_Courses": {},
#         "Sea_Service_Details": {},
#         "Specialised_Experience": {},
#         "References": {},
#         "Declaration": {},
#         "Office_Use_Only": {},
#         # NEW CATEGORIES
#         "Physical_Measurements": {},
#         "Language_Skills": {},
#         "Medical_History": {},
#         "Assessments": {},
#         "Competency_Tests": {},
#         "error": "All parsing methods failed", 
#         "raw_output": str(raw_result)[:500]
#     }









import json
import re
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_ollama import OllamaLLM

# 1. Define schema fields - UPDATED WITH ALL NEW CATEGORIES
response_schemas = [
    ResponseSchema(name="Personal_Details", description="Personal details of the applicant"),
    ResponseSchema(name="Education", description="Education and language skills"),
    ResponseSchema(name="Contact_Details", description="Contact information"),
    ResponseSchema(name="Travel_Documents", description="Passport, seaman book, etc."),
    ResponseSchema(name="Professional_Qualifications", description="Certificates of competency and qualifications"),
    ResponseSchema(name="Next_of_Kin_Emergency_Contact", description="Next of kin or emergency contacts"),
    ResponseSchema(name="Health_Certificates_Vaccinations", description="Health certificates and vaccinations"),
    ResponseSchema(name="Covid_19_Vaccination", description="Covid-19 vaccination details"),
    ResponseSchema(name="Marine_Courses", description="Marine and safety training courses"),
    ResponseSchema(name="Sea_Service_Details", description="Details of sea service records"),
    ResponseSchema(name="Specialised_Experience", description="Specialised experiences if any"),
    ResponseSchema(name="References", description="References provided by the applicant"),
    ResponseSchema(name="Declaration", description="Declaration, health questions, signature, date"),
    ResponseSchema(name="Office_Use_Only", description="Office assessment and signature"),
    # NEW CATEGORIES ADDED
    ResponseSchema(name="Physical_Measurements", description="Physical measurements like overall size, shirt size, trouser size, shoes size"),
    ResponseSchema(name="Language_Skills", description="Language proficiency including English level and other languages"),
    ResponseSchema(name="Medical_History", description="Medical history including disease history, accident history, psychiatric treatment, addiction history"),
    ResponseSchema(name="Assessments", description="Various assessments and test results including Marlins test"),
    ResponseSchema(name="Competency_Tests", description="Competency test results and certifications"),
    ResponseSchema(name="Applied_Position_Info", description="Information about the position applied for, expected salary, availability date"),
]

# 2. Create the parser
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# 3. Format instructions (JSON schema instructions)
format_instructions = output_parser.get_format_instructions()


def repair_json_string(text: str) -> str:
    """Fix common JSON formatting errors from LLM output."""
    
    if hasattr(text, 'content'):
        text = text.content
    else:
        text = str(text)
    
    # Remove markdown code fences
    text = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE)
    
    # Remove any control characters that cause parsing issues
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    # Fix broken syntax - ensure proper JSON structure
    # Remove any trailing incomplete parts
    brace_count = 0
    last_complete_pos = 0
    
    for i, char in enumerate(text):
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
            if brace_count == 0:
                last_complete_pos = i + 1
    
    # Truncate to last complete JSON object
    if last_complete_pos > 0:
        text = text[:last_complete_pos]
    
    # Fix trailing commas
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)
    
    # Fix multiple commas
    text = re.sub(r',\s*,+', ',', text)
    
    return text


def extract_json_data_manually(text: str) -> dict:
    """Manually extract data from malformed JSON when parsing fails."""
    result = {}
    
    # Define the expected keys - UPDATED WITH ALL NEW CATEGORIES
    expected_keys = [
        "Personal_Details", "Education", "Contact_Details", "Travel_Documents",
        "Professional_Qualifications", "Next_of_Kin_Emergency_Contact",
        "Health_Certificates_Vaccinations", "Covid_19_Vaccination", "Marine_Courses",
        "Sea_Service_Details", "Specialised_Experience", "References",
        "Declaration", "Office_Use_Only",
        # NEW CATEGORIES
        "Physical_Measurements", "Language_Skills", "Medical_History", 
        "Assessments", "Competency_Tests", "Applied_Position_Info"
    ]
    
    for key in expected_keys:
        result[key] = {}
    
    # Extract personal details
    name_match = re.search(r'"name":\s*"([^"]*)"', text, re.IGNORECASE)
    if name_match:
        result["Personal_Details"]["name"] = name_match.group(1)
    
    email_match = re.search(r'"email":\s*"([^"]*@[^"]*)"', text, re.IGNORECASE)
    if email_match:
        result["Personal_Details"]["email"] = email_match.group(1)
        result["Contact_Details"]["email"] = email_match.group(1)
    
    phone_match = re.search(r'"phone":\s*"([^"]*)"', text, re.IGNORECASE)
    if phone_match:
        result["Personal_Details"]["phone"] = phone_match.group(1)
        result["Contact_Details"]["phone"] = phone_match.group(1)
    
    nationality_match = re.search(r'"nationality":\s*"([^"]*)"', text, re.IGNORECASE)
    if nationality_match:
        result["Personal_Details"]["nationality"] = nationality_match.group(1)
    
    birth_date_match = re.search(r'"birth_date":\s*"([^"]*)"', text, re.IGNORECASE)
    if birth_date_match:
        result["Personal_Details"]["birth_date"] = birth_date_match.group(1)
    
    address_match = re.search(r'"address":\s*"([^"]*)"', text, re.IGNORECASE)
    if address_match:
        result["Personal_Details"]["address"] = address_match.group(1)
        result["Contact_Details"]["address"] = address_match.group(1)
    
    # Extract physical measurements
    overall_size_match = re.search(r'"overall[_\s]*size":\s*"([^"]*)"', text, re.IGNORECASE)
    if overall_size_match:
        result["Physical_Measurements"]["overall_size"] = overall_size_match.group(1)
    
    shirt_size_match = re.search(r'"shirt[_\s]*size":\s*"([^"]*)"', text, re.IGNORECASE)
    if shirt_size_match:
        result["Physical_Measurements"]["shirt_size"] = shirt_size_match.group(1)
    
    # Extract language skills
    english_match = re.search(r'"english[_\s]*level":\s*"([^"]*)"', text, re.IGNORECASE)
    if english_match:
        result["Language_Skills"]["english_language_level"] = english_match.group(1)
    
    # Extract Marlins test data
    marlins_match = re.search(r'"marlins[_\s]*test[_\s]*result":\s*"([^"]*)"', text, re.IGNORECASE)
    if marlins_match:
        result["Assessments"]["marlins_test_result"] = marlins_match.group(1)
    
    # Extract applied position info
    position_match = re.search(r'"position[_\s]*applied":\s*"([^"]*)"', text, re.IGNORECASE)
    if position_match:
        result["Applied_Position_Info"]["position_applied"] = position_match.group(1)
    
    salary_match = re.search(r'"expected[_\s]*salary":\s*"([^"]*)"', text, re.IGNORECASE)
    if salary_match:
        result["Applied_Position_Info"]["expected_salary"] = salary_match.group(1)
    
    return result


def convert_text_to_json(extracted_text: str) -> dict:
    """
    Convert extracted document text into structured JSON using Ollama.
    Returns a dictionary, not a string.
    """
    llm = OllamaLLM(model="llama3.2:1b", temperature=0)

    # Truncate text if too long
    max_chars = 3000
    truncated_text = extracted_text[:max_chars] if len(extracted_text) > max_chars else extracted_text

    prompt = PromptTemplate(
        template="""You are a JSON generator. Extract information from this CV text and return ONLY valid JSON.

CV Text:
{document}

Return a JSON object with these keys (use empty object {{}} if no data found):
- Personal_Details (name, birth_date, nationality, address, email, phone)
- Education (schools, languages)
- Contact_Details (email, phone, address)
- Travel_Documents (passport details, seaman book)
- Professional_Qualifications (certificates)
- Sea_Service_Details (ship experience)
- Marine_Courses (training)
- Physical_Measurements (overall_size, shirt_size, trouser_size, shoes_size)
- Language_Skills (english_language_level, other_language, other_language_level)
- Medical_History (disease_history, accident_history, psychiatric_treatment_history, addiction_history)
- Assessments (marlins_test_result, marlins_test_issued_date, marlins_test_issued_at, marlins_test_issued_by)
- Competency_Tests (test results and certifications)
- Applied_Position_Info (position_applied, expected_salary, availability_date)

CRITICAL RULES:
1. Return ONLY the JSON object, no explanations
2. Use double quotes for all strings
3. Do NOT escape quotes inside values
4. Do NOT use parentheses in JSON
5. Use simple strings, not nested quotes
6. Extract size information (L, M, XL, 42, etc.) to Physical_Measurements
7. Extract language proficiency to Language_Skills
8. Extract medical history to Medical_History
9. Extract test results to Assessments and Competency_Tests
10. Extract position applied for, salary expectations to Applied_Position_Info

Example format:
{{
  "Personal_Details": {{
    "name": "John Doe",
    "birth_date": "01/01/1990"
  }},
  "Physical_Measurements": {{
    "overall_size": "L",
    "shirt_size": "M"
  }},
  "Language_Skills": {{
    "english_language_level": "Good"
  }},
  "Applied_Position_Info": {{
    "position_applied": "Marine Engineer",
    "expected_salary": "5000 USD"
  }},
  "Education": {{}}
}}
""",
        input_variables=["document"],
    )

    chain = prompt | llm
    raw_result = chain.invoke({"document": truncated_text})
    
    print("=" * 80)
    print("RAW LLM OUTPUT:")
    print(raw_result)
    print("=" * 80)
    
    # Handle the case where raw_result might already be a dict
    if isinstance(raw_result, dict):
        print("LLM returned a dictionary directly")
        result = raw_result
    else:
        # More aggressive cleaning
        try:
            # Extract just the JSON part if there's extra text
            json_match = re.search(r'\{.*\}', str(raw_result), re.DOTALL)
            if json_match:
                raw_result = json_match.group(0)
            
            cleaned = repair_json_string(str(raw_result))
            print(f"Cleaned JSON length: {len(cleaned)}")
            print(f"Cleaned text preview: {cleaned[:200]}...")
            
            result = json.loads(cleaned)
            print("Successfully parsed JSON")
            
        except Exception as e:
            print(f"Parsing failed: {e}")
            print(f"Attempting manual extraction...")
            
            # Try manual extraction as fallback
            try:
                result = extract_json_data_manually(str(raw_result))
                print("Manual extraction successful")
            except Exception as manual_error:
                print(f"Manual extraction also failed: {manual_error}")
                result = {
                    "Personal_Details": {},
                    "Education": {},
                    "Contact_Details": {},
                    "Travel_Documents": {},
                    "Professional_Qualifications": {},
                    "Next_of_Kin_Emergency_Contact": {},
                    "Health_Certificates_Vaccinations": {},
                    "Covid_19_Vaccination": {},
                    "Marine_Courses": {},
                    "Sea_Service_Details": {},
                    "Specialised_Experience": {},
                    "References": {},
                    "Declaration": {},
                    "Office_Use_Only": {},
                    # NEW CATEGORIES
                    "Physical_Measurements": {},
                    "Language_Skills": {},
                    "Medical_History": {},
                    "Assessments": {},
                    "Competency_Tests": {},
                    "Applied_Position_Info": {},
                    "error": str(e),
                    "raw_output": str(raw_result)[:500]
                }
    
    # Ensure all expected keys exist - UPDATED WITH ALL NEW CATEGORIES
    expected_keys = [
        "Personal_Details", "Education", "Contact_Details", "Travel_Documents",
        "Professional_Qualifications", "Next_of_Kin_Emergency_Contact",
        "Health_Certificates_Vaccinations", "Covid_19_Vaccination", "Marine_Courses",
        "Sea_Service_Details", "Specialised_Experience", "References",
        "Declaration", "Office_Use_Only",
        # NEW CATEGORIES
        "Physical_Measurements", "Language_Skills", "Medical_History", 
        "Assessments", "Competency_Tests", "Applied_Position_Info"
    ]
    
    for key in expected_keys:
        if key not in result:
            result[key] = {}
    
    print(f"Final result type: {type(result)}")
    print(f"Final result keys: {list(result.keys())}")
    
    return result


# Alternative function with more aggressive JSON cleaning
def convert_text_to_json_robust(extracted_text: str) -> dict:
    """
    More robust version with additional JSON repair strategies.
    Always returns a dictionary.
    """
    
    llm = OllamaLLM(model="llama3.2:1b")

    prompt = PromptTemplate(
        template="""
You are an expert information extraction system.

Extract structured data from the following CV text and return it as valid JSON.

Text:
{document}

CRITICAL: Return ONLY a valid JSON object. No explanations, no markdown, no extra text.

Extract information for these categories:
- Personal_Details: Full name, nationality, date of birth, etc.
- Education: Educational background and language skills
- Contact_Details: Address, phone, email
- Travel_Documents: Passport details, seaman's book
- Professional_Qualifications: Certificates and licenses
- Next_of_Kin_Emergency_Contact: Emergency contact information
- Health_Certificates_Vaccinations: Health and vaccination records
- Covid_19_Vaccination: COVID vaccination details
- Marine_Courses: Maritime training and courses
- Sea_Service_Details: Previous sea service experience
- Specialised_Experience: Any specialized skills or experience
- References: Professional references
- Declaration: Declarations and signatures
- Office_Use_Only: Internal office notes
- Physical_Measurements: Overall size, shirt size, trouser size, shoes size
- Language_Skills: English proficiency level, other languages
- Medical_History: Disease history, accident history, psychiatric treatment, addiction history
- Assessments: Marlins test results and other assessments
- Competency_Tests: Various competency test results
- Applied_Position_Info: Position applied for, expected salary, availability date

Use empty strings "" for missing information.
""",
        input_variables=["document"],
    )

    chain = prompt | llm
    raw_result = chain.invoke({"document": extracted_text})
    
    # Handle different result types
    if isinstance(raw_result, dict):
        return raw_result
    
    # Multiple parsing attempts
    parsing_attempts = [
        lambda x: json.loads(str(x)),
        lambda x: json.loads(repair_json_string(str(x))),
        lambda x: extract_json_data_manually(str(x)),
    ]
    
    for attempt in parsing_attempts:
        try:
            result = attempt(raw_result)
            if isinstance(result, dict):
                return result
        except Exception:
            continue
    
    # Final fallback - always return a dict - UPDATED WITH ALL NEW CATEGORIES
    return {
        "Personal_Details": {},
        "Education": {},
        "Contact_Details": {},
        "Travel_Documents": {},
        "Professional_Qualifications": {},
        "Next_of_Kin_Emergency_Contact": {},
        "Health_Certificates_Vaccinations": {},
        "Covid_19_Vaccination": {},
        "Marine_Courses": {},
        "Sea_Service_Details": {},
        "Specialised_Experience": {},
        "References": {},
        "Declaration": {},
        "Office_Use_Only": {},
        # NEW CATEGORIES
        "Physical_Measurements": {},
        "Language_Skills": {},
        "Medical_History": {},
        "Assessments": {},
        "Competency_Tests": {},
        "Applied_Position_Info": {},
        "error": "All parsing methods failed", 
        "raw_output": str(raw_result)[:500]
    }