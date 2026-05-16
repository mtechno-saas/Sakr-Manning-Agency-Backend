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









# import json
# import re
# from langchain.prompts import PromptTemplate
# from langchain.output_parsers import StructuredOutputParser, ResponseSchema
# from langchain_ollama import OllamaLLM

# # 1. Define schema fields - UPDATED WITH ALL NEW CATEGORIES
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
#     ResponseSchema(name="Applied_Position_Info", description="Information about the position applied for, expected salary, availability date"),
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
    
#     # Define the expected keys - UPDATED WITH ALL NEW CATEGORIES
#     expected_keys = [
#         "Personal_Details", "Education", "Contact_Details", "Travel_Documents",
#         "Professional_Qualifications", "Next_of_Kin_Emergency_Contact",
#         "Health_Certificates_Vaccinations", "Covid_19_Vaccination", "Marine_Courses",
#         "Sea_Service_Details", "Specialised_Experience", "References",
#         "Declaration", "Office_Use_Only",
#         # NEW CATEGORIES
#         "Physical_Measurements", "Language_Skills", "Medical_History", 
#         "Assessments", "Competency_Tests", "Applied_Position_Info"
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
    
#     # Extract applied position info
#     position_match = re.search(r'"position[_\s]*applied":\s*"([^"]*)"', text, re.IGNORECASE)
#     if position_match:
#         result["Applied_Position_Info"]["position_applied"] = position_match.group(1)
    
#     salary_match = re.search(r'"expected[_\s]*salary":\s*"([^"]*)"', text, re.IGNORECASE)
#     if salary_match:
#         result["Applied_Position_Info"]["expected_salary"] = salary_match.group(1)
    
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
# - Applied_Position_Info (position_applied, expected_salary, availability_date)

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
# 10. Extract position applied for, salary expectations to Applied_Position_Info

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
#   "Applied_Position_Info": {{
#     "position_applied": "Marine Engineer",
#     "expected_salary": "5000 USD"
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
#                     "Applied_Position_Info": {},
#                     "error": str(e),
#                     "raw_output": str(raw_result)[:500]
#                 }
    
#     # Ensure all expected keys exist - UPDATED WITH ALL NEW CATEGORIES
#     expected_keys = [
#         "Personal_Details", "Education", "Contact_Details", "Travel_Documents",
#         "Professional_Qualifications", "Next_of_Kin_Emergency_Contact",
#         "Health_Certificates_Vaccinations", "Covid_19_Vaccination", "Marine_Courses",
#         "Sea_Service_Details", "Specialised_Experience", "References",
#         "Declaration", "Office_Use_Only",
#         # NEW CATEGORIES
#         "Physical_Measurements", "Language_Skills", "Medical_History", 
#         "Assessments", "Competency_Tests", "Applied_Position_Info"
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
# - Applied_Position_Info: Position applied for, expected salary, availability date

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
    
#     # Final fallback - always return a dict - UPDATED WITH ALL NEW CATEGORIES
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
#         "Applied_Position_Info": {},
#         "error": "All parsing methods failed", 
#         "raw_output": str(raw_result)[:500]
#     }











"""
FIXED VERSION of document_to_json.py
This version includes:
1. Detailed schema with specific field descriptions
2. Improved LLM prompt with examples
3. Better handling of arrays for multiple items
4. Larger context window
5. Better error handling
"""

import re
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_ollama import OllamaLLM


# IMPROVED SCHEMA WITH DETAILED DESCRIPTIONS
response_schemas = [
    ResponseSchema(
        name="Personal_Details",
        description="""Personal details including:
        - Full_Name (complete name)
        - Date_Of_Birth (format: DD/MM/YYYY or YYYY-MM-DD)
        - Place_Of_Birth (city/country)
        - Nationality
        - Marital_Status (Single/Married/Divorced)
        - Height_Cm, Weight_Kg
        - Overall_Size, Shirt_Size, Trouser_Size, Shoes_Size
        - Nearest_Port
        - Expected_Salary
        - Available_Date
        - Register_Code"""
    ),
    ResponseSchema(
        name="Education",
        description="""Education details including:
        - College_School (name of institution)
        - Marine_Test (object with: Issued_Date, Result_Percent, Issued_By_Authority, Issued_At)
        - English_Language (proficiency level)
        - Other_Languages (array of languages)"""
    ),
    ResponseSchema(
        name="Contact_Details",
        description="""Contact information including:
        - Home_Address_City (full address)
        - Email
        - Mobile_Tel (phone number with country code)"""
    ),
    ResponseSchema(
        name="Travel_Documents",
        description="""Array of travel documents. Each document should include:
        - Type (Passport, Seaman Book, Other Seaman Book)
        - Document_No (document number)
        - Register_Code
        - ISS_Date (issue date)
        - Exp_Date (expiry date)
        - ISS_By_Authority (issuing authority)
        - Place_of_Issue
        Extract ALL documents found in the CV."""
    ),
    ResponseSchema(
        name="Professional_Qualifications",
        description="""Array of professional certificates. Each certificate should include:
        - Certificate_Name (e.g., COC, GOC)
        - Number (certificate number)
        - Register_Code
        - Issue_Date
        - Expiry_Date
        - Issued_By (issuing authority)
        - Issued_At (place of issue)
        Extract ALL certificates found."""
    ),
    ResponseSchema(
        name="Next_of_Kin_Emergency_Contact",
        description="""Next of kin/emergency contact including:
        - Full_Name
        - Relationship (e.g., SON, WIFE, FATHER)
        - Address
        - Address_Country
        - Tel_No
        - Mobile
        - Email"""
    ),
    ResponseSchema(
        name="Health_Certificates_Vaccinations",
        description="""Array of health certificates and vaccinations. Each should include:
        - Flag_State (type: International Medical, Yellow Fever, Cholera, etc.)
        - Number (certificate number)
        - Register_Code
        - Issue_Date
        - Expiry_Date
        - Issued_By (issuing authority)
        - Issued_At (place of issue)
        Extract ALL health certificates and vaccinations."""
    ),
    ResponseSchema(
        name="Covid_19_Vaccination",
        description="""COVID-19 vaccination details including:
        - Vaccination_Name (e.g., ASTRAZENECA, PFIZER, MODERNA)
        - First_Dose (date of first dose)
        - Second_Dose (date of second dose)
        - Other_Doses_or_Remarks (booster doses or notes)"""
    ),
    ResponseSchema(
        name="Marine_Courses",
        description="""Array of marine training courses. Each course should include:
        - Course_Name (full course name)
        - Number (certificate number)
        - Register_Code
        - Issue_Date
        - Expiry_Date
        - Issued_By_At (issuing authority and location)
        Extract ALL courses found, including STCW courses, safety training, specialized courses."""
    ),
    ResponseSchema(
        name="Sea_Service_Details",
        description="""Array of sea service records. Each record should include:
        - Company_Name
        - Rank (position held)
        - Vessel_Name
        - Vessel_Name_IMO_Number
        - Flag (vessel flag state)
        - Signed_On (embarkation date)
        - Signed_Off (disembarkation date)
        - Period (duration)
        - Vessel_Type (Passenger, Cargo, Tanker, etc.)
        - DWT_GRT (deadweight tonnage / gross registered tonnage)
        - Engine_Type (engine manufacturer and model)
        - BH_KW (brake horsepower / kilowatts)
        - Reason_for_Sign_off
        Extract ALL sea service records in chronological order."""
    ),
    ResponseSchema(
        name="Specialised_Experience",
        description="Array of any specialized experiences or skills not covered in other sections"
    ),
    ResponseSchema(
        name="References",
        description="Array of professional references with contact details"
    ),
    ResponseSchema(
        name="Declaration",
        description="""Declaration section including:
        - Health_Questions (object with: Disease_likely_to_render_unfit, Accident_rendering_disabled, Psychiatric_treatment, Addicted_to_alcohol_or_drugs)
        - Consent_Statement
        - Signature
        - Date"""
    ),
    ResponseSchema(
        name="Office_Use_Only",
        description="""Office use section including:
        - Initial_assessment_of_applicant
        - Comments
        - Responsible_person
        - Name_Signature
        - Date"""
    ),
]

# Create the parser
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# Format instructions
format_instructions = output_parser.get_format_instructions()


def normalize_for_serializer(data):
    """
    Keep arrays but also add flattened fields for easy serializer access.
    """
    if not isinstance(data, dict):
        return data
    
    normalized = data.copy()
    
    # Extract passport and seaman book from Travel_Documents array
    if 'Travel_Documents' in normalized and isinstance(normalized['Travel_Documents'], list):
        docs = normalized['Travel_Documents']
        
        passport = next((d for d in docs if d.get('Type') == 'Passport'), {})
        seaman = next((d for d in docs if d.get('Type') == 'Seaman Book'), {})
        
        # Add flattened fields (for backward compatibility)
        normalized['passport_info'] = passport
        normalized['seaman_book_info'] = seaman
    
    # Extract COC and GOC from Professional_Qualifications array
    if 'Professional_Qualifications' in normalized and isinstance(normalized['Professional_Qualifications'], list):
        certs = normalized['Professional_Qualifications']
        
        coc = next((c for c in certs if 'COC' in c.get('Certificate_Name', '')), {})
        goc = next((c for c in certs if 'GOC' in c.get('Certificate_Name', '')), {})
        
        normalized['coc_info'] = coc
        normalized['goc_info'] = goc
    
    # Extract medical certificates
    if 'Health_Certificates_Vaccinations' in normalized and isinstance(normalized['Health_Certificates_Vaccinations'], list):
        certs = normalized['Health_Certificates_Vaccinations']
        
        medical = next((c for c in certs if 'Medical' in c.get('Flag_State', '')), {})
        yellow_fever = next((c for c in certs if 'Yellow Fever' in c.get('Flag_State', '')), {})
        
        normalized['medical_certificate_info'] = medical
        normalized['yellow_fever_info'] = yellow_fever
    
    return normalized



def repair_json_string(text: str) -> str:
    """Fix common JSON formatting errors from LLM output."""
    
    if hasattr(text, 'content'):
        text = text.content
    else:
        text = str(text)
    
    # Remove markdown code fences
    text = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE)
    text = re.sub(r"^```|```$", "", text.strip(), flags=re.MULTILINE)
    
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


def extract_structured_data_from_text(text: str) -> dict:
    """
    Enhanced extraction using regex patterns for structured data.
    This helps capture data that LLM might miss.
    """
    result = {}
    
    # Extract passport information
    passport_match = re.search(r'passport[:\s]+([A-Z0-9]+)', text, re.IGNORECASE)
    if passport_match:
        result['passport_number'] = passport_match.group(1)
    
    # Extract seaman book
    seaman_match = re.search(r'seaman[\'s\s]+book[:\s]+([A-Z0-9]+)', text, re.IGNORECASE)
    if seaman_match:
        result['seaman_book_number'] = seaman_match.group(1)
    
    # Extract dates (various formats)
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # DD/MM/YYYY
        r'\d{2}-\d{2}-\d{4}',  # DD-MM-YYYY
    ]
    
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text))
    result['found_dates'] = dates
    
    # Extract email
    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    if email_match:
        result['email'] = email_match.group(0)
    
    # Extract phone numbers
    phone_patterns = [
        r'\+\d{1,3}[\s-]?\d{3,}[\s-]?\d{3,}',  # International format
        r'\d{3}[\s-]?\d{3}[\s-]?\d{4}',  # Local format
    ]
    
    phones = []
    for pattern in phone_patterns:
        phones.extend(re.findall(pattern, text))
    result['found_phones'] = phones
    
    return result


def convert_text_to_json(extracted_text: str) -> dict:
    """
    Convert extracted document text into structured JSON using Ollama.
    Returns a dictionary with all extracted data.
    """
    
    # VALIDATION: Check if this is actually a maritime CV before processing
    def is_valid_maritime_cv(text: str) -> bool:
        """
        Check if the document contains maritime CV indicators.
        Returns False if the document is NOT a maritime CV.
        """
        text_lower = text.lower()
        
        # Maritime-specific keywords that should be present in a valid CV
        maritime_keywords = [
            'passport', 'seaman', 'coc', 'goc', 'rank', 'vessel', 'ship',
            'marine', 'maritime', 'stcw', 'certificate', 'sea service',
            'nationality', 'date of birth', 'personal details', 'marital status',
            'next of kin', 'emergency contact', 'vaccination', 'health certificate',
            'fire fighting', 'survival', 'sailor', 'officer', 'engineer',
            'captain', 'chief', 'deck', 'engine', 'flag state', 'imo',
            'dwt', 'grt', 'signed on', 'signed off', 'full name', 'port',
            'cv', 'resume', 'curriculum vitae', 'application form'
        ]
        
        # Count how many maritime keywords are found
        keyword_count = sum(1 for keyword in maritime_keywords if keyword in text_lower)
        
        # Require at least 5 maritime keywords to consider it a valid CV
        # Also check for minimum text length (a real CV should have substantial content)
        min_keywords = 5
        min_length = 200  # At least 200 characters of actual content
        
        is_valid = keyword_count >= min_keywords and len(text.strip()) >= min_length
        
        print(f"CV Validation: Found {keyword_count} maritime keywords, text length: {len(text.strip())}")
        print(f"CV Validation Result: {'VALID' if is_valid else 'INVALID - NOT A MARITIME CV'}")
        
        return is_valid
    
    # Check if document is a valid maritime CV
    if not is_valid_maritime_cv(extracted_text):
        print("=" * 80)
        print("⚠️ DOCUMENT IS NOT A VALID MARITIME CV - RETURNING EMPTY DATA")
        print("=" * 80)
        
        # Return empty structured data without calling LLM
        return {
            "Personal_Details": {},
            "Education": {},
            "Contact_Details": {},
            "Travel_Documents": [],
            "Professional_Qualifications": [],
            "Next_of_Kin_Emergency_Contact": {},
            "Health_Certificates_Vaccinations": [],
            "Covid_19_Vaccination": {},
            "Marine_Courses": [],
            "Sea_Service_Details": [],
            "Specialised_Experience": [],
            "References": [],
            "Declaration": {},
            "Office_Use_Only": {},
            "validation_error": "Document does not appear to be a maritime CV. No data extracted."
        }
    
    # Use a larger model for better extraction
    # Change from llama3.2:1b to llama3.2:3b or llama3:8b if available
    llm = OllamaLLM(model="llama3.2:1b", temperature=0)
    
    # Increase context window - process more text
    max_chars = 8000  # Increased from 3000
    truncated_text = extracted_text[:max_chars] if len(extracted_text) > max_chars else extracted_text
    
    # IMPROVED PROMPT WITH DETAILED INSTRUCTIONS AND EXAMPLES
    prompt = PromptTemplate(
        template="""You are an expert data extraction specialist for maritime CV/resume documents. 
Extract ALL information from the CV text and return it as a valid JSON object.

CV TEXT:
{document}

EXTRACTION INSTRUCTIONS:

1. **Personal_Details**: Extract full name, date of birth, place of birth, nationality, marital status, physical measurements, nearest port, expected salary, available date, register code.

2. **Education**: Extract educational background, marine test results, language skills.

3. **Contact_Details**: Extract home address, email, mobile telephone.

4. **Travel_Documents**: Extract ALL travel documents as an ARRAY. Each document should include:
   - Type (Passport, Seaman Book, etc.)
   - Document number
   - Issue date and expiry date
   - Issuing authority and place
   Example: [
     {{{{"Type": "Passport", "Document_No": "A24348496", "ISS_Date": "2019-08-18", "Exp_Date": "2026-02-17"}}}},
     {{{{"Type": "Seaman Book", "Document_No": "S00034684", "ISS_Date": "2023-09-14", "Exp_Date": "2028-09-10"}}}}
   ]

5. **Professional_Qualifications**: Extract ALL certificates (COC, GOC, etc.) as an ARRAY with certificate name, number, dates, issuing authority.

6. **Next_of_Kin_Emergency_Contact**: Extract emergency contact person's full name, relationship, address, phone, email.

7. **Health_Certificates_Vaccinations**: Extract ALL health certificates and vaccinations as an ARRAY:
   - International Medical Certificate
   - Yellow Fever
   - Cholera
   - Other vaccinations
   Include certificate numbers, issue/expiry dates, issuing authority.

8. **Covid_19_Vaccination**: Extract COVID vaccine name (ASTRAZENECA, PFIZER, etc.), first dose date, second dose date, booster information.

9. **Marine_Courses**: Extract ALL marine training courses as an ARRAY. Look for:
   - STCW courses (Personal Survival, Fire Fighting, First Aid, etc.)
   - Security training (SSO, Security Awareness)
   - Specialized courses (ECDIS, GMDSS, Radar, ARPA, etc.)
   - Passenger ship courses
   - Engineering courses
   For each course include: Course_Name, Number, Issue_Date, Expiry_Date, Issued_By_At

10. **Sea_Service_Details**: Extract ALL sea service records as an ARRAY. For each vessel assignment include:
    - Company name
    - Rank/position
    - Vessel name and IMO number
    - Flag state
    - Sign-on and sign-off dates
    - Vessel type, DWT/GRT, engine type, BH/KW
    - Reason for sign-off

11. **Specialised_Experience**: Extract any specialized skills or experiences.

12. **References**: Extract professional references.

13. **Declaration**: Extract health declaration questions, consent statement, signature, date.

14. **Office_Use_Only**: Extract office assessment, comments, responsible person, date.

CRITICAL RULES:
- Return ONLY valid JSON, no explanations
- Use double quotes for all strings
- For arrays, use [] syntax: "Travel_Documents": [{{...}}, {{...}}]
- If no data found for a field, use empty string "" for strings, empty array [] for arrays, empty object {{{{}}}} for objects
- Extract dates in the format found in the document
- Extract ALL instances of multi-item categories (documents, certificates, courses, sea service)
- Do NOT truncate or summarize - extract complete information
- If the uploaded CV text is missing, unstructured, incomplete, or does not explicitly like the provided features do not extract any data from the document

IMPORTANT: Extract ACTUAL DATA from the CV text above. DO NOT use placeholder text.
DO NOT return "[EXTRACT_FROM_CV]" or any placeholder - return the REAL values found in the document.
If a field is not found in the CV, use an empty string "".

OUTPUT FORMAT (replace with ACTUAL values from the CV):
{{{{
  "Personal_Details": {{{{
    "Full_Name": "<actual name from CV>",
    "Date_Of_Birth": "<actual date>",
    "Place_Of_Birth": "<actual place>",
    "Nationality": "<actual nationality>",
    "Marital_Status": "<actual status>",
    "Nearest_Port": "<actual port>",
    "Register_Code": "<actual code>"
  }}}},
  "Contact_Details": {{{{
    "Home_Address_City": "<actual address>",
    "Email": "<actual email>",
    "Mobile_Tel": "<actual phone>"
  }}}},
  "Travel_Documents": [
    {{{{ "Type": "Passport", "Document_No": "<actual number>", "ISS_Date": "<actual date>", "Exp_Date": "<actual date>", "ISS_By_Authority": "<actual authority>" }}}},
    {{{{ "Type": "Seaman Book", "Document_No": "<actual number>", "ISS_Date": "<actual date>", "Exp_Date": "<actual date>", "ISS_By_Authority": "<actual authority>", "Place_of_Issue": "<actual place>" }}}}
  ],
  "Professional_Qualifications": [
    {{{{ "Certificate_Name": "<actual cert name>", "Number": "<actual number>", "Issue_Date": "<actual date>", "Expiry_Date": "<actual date>", "Issued_By": "<actual authority>", "Issued_At": "<actual place>" }}}}
  ],
  "Next_of_Kin_Emergency_Contact": {{{{
    "Full_Name": "<actual name>",
    "Relationship": "<actual relationship>",
    "Mobile": "<actual phone>"
  }}}},
  "Health_Certificates_Vaccinations": [
    {{{{ "Flag_State": "<actual type>", "Number": "<actual number>", "Issue_Date": "<actual date>", "Expiry_Date": "<actual date>", "Issued_By": "<actual authority>" }}}}
  ],
  "Covid_19_Vaccination": {{{{
    "Vaccination_Name": "<actual vaccine name>",
    "First_Dose": "<actual date>",
    "Second_Dose": "<actual date>"
  }}}},
  "Marine_Courses": [
    {{{{ "Course_Name": "<actual course name>", "Number": "<actual number>", "Issue_Date": "<actual date>", "Expiry_Date": "<actual date>", "Issued_By_At": "<actual authority>" }}}}
  ],
  "Sea_Service_Details": [
    {{{{ "Company_Name": "<actual company>", "Rank": "<actual rank>", "Vessel_Name": "<actual vessel>", "Flag": "<actual flag>", "Signed_On": "<actual date>", "Signed_Off": "<actual date>", "Vessel_Type": "<actual type>", "Engine_Type": "<actual engine>", "Reason_for_Sign_off": "<actual reason>" }}}}
  ],
  "Specialised_Experience": [],
  "References": [],
  "Declaration": {{{{}}}},
  "Office_Use_Only": {{{{}}}},
  "Education": {{{{}}}}
}}}}

CRITICAL: Replace all <...> placeholders above with ACTUAL DATA extracted from the CV text. 
DO NOT include angle brackets < > in your output.
If information is not found, use empty string "".

Now extract ALL information from the CV text and return the JSON with REAL DATA:
""",
        input_variables=["document"],
    )
    
    chain = prompt | llm
    
    try:
        print("=" * 80)
        print("INVOKING LLM FOR DATA EXTRACTION...")
        print(f"Text length: {len(truncated_text)} characters")
        print("=" * 80)
        
        raw_result = chain.invoke({"document": truncated_text})
        
        print("=" * 80)
        print("RAW LLM OUTPUT:")
        print(str(raw_result)[:1000])  # Print first 1000 chars
        print("..." if len(str(raw_result)) > 1000 else "")
        print("=" * 80)
        
        # Handle the case where raw_result might already be a dict
        if isinstance(raw_result, dict):
            print("✅ LLM returned a dictionary directly")
            result = raw_result
        else:
            # Extract JSON from the response
            try:
                # Try to find JSON object in the response
                json_match = re.search(r'\{.*\}', str(raw_result), re.DOTALL)
                if json_match:
                    raw_result = json_match.group(0)
                
                cleaned = repair_json_string(str(raw_result))
                print(f"Cleaned JSON length: {len(cleaned)}")
                
                result = json.loads(cleaned)
                print("✅ Successfully parsed JSON")
                
                # POST-PROCESSING: Remove any placeholder values that the LLM copied
                def clean_placeholders(obj):
                    """Recursively clean placeholder values from the result."""
                    placeholder_patterns = [
                        r'^\[EXTRACT_FROM_CV\]$',
                        r'^\[extract_from_cv\]$',
                        r'^<actual.*>$',
                        r'^<.*>$',  # Any angle bracket placeholder
                        r'^\[.*\]$',  # Any square bracket placeholder (but not arrays)
                    ]
                    
                    if isinstance(obj, dict):
                        cleaned = {}
                        for key, value in obj.items():
                            cleaned[key] = clean_placeholders(value)
                        return cleaned
                    elif isinstance(obj, list):
                        return [clean_placeholders(item) for item in obj]
                    elif isinstance(obj, str):
                        # Check if this is a placeholder value
                        for pattern in placeholder_patterns:
                            if re.match(pattern, obj, re.IGNORECASE):
                                print(f"⚠️ Removing placeholder value: {obj}")
                                return ""  # Replace with empty string
                        return obj
                    else:
                        return obj
                
                result = clean_placeholders(result)
                print("✅ Cleaned any placeholder values")
                
            except Exception as e:
                print(f"❌ Parsing failed: {e}")
                print("Attempting regex-based extraction...")
                
                # Fallback: Use regex to extract structured data
                regex_data = extract_structured_data_from_text(truncated_text)
                print(f"Regex extracted: {regex_data}")
                
                # Return minimal structure with regex-extracted data
                result = {
                    "Personal_Details": {
                        "email": regex_data.get('email', '')
                    },
                    "Contact_Details": {
                        "email": regex_data.get('email', ''),
                        "phones": regex_data.get('found_phones', [])
                    },
                    "Travel_Documents": [],
                    "Professional_Qualifications": [],
                    "Next_of_Kin_Emergency_Contact": {},
                    "Health_Certificates_Vaccinations": [],
                    "Covid_19_Vaccination": {},
                    "Marine_Courses": [],
                    "Sea_Service_Details": [],
                    "Specialised_Experience": [],
                    "References": [],
                    "Declaration": {},
                    "Office_Use_Only": {},
                    "Education": {},
                    "error": str(e),
                    "raw_output": str(raw_result)[:500]
                }
    
    except Exception as e:
        print(f"❌ LLM invocation failed: {e}")
        result = {
            "Personal_Details": {},
            "Education": {},
            "Contact_Details": {},
            "Travel_Documents": [],
            "Professional_Qualifications": [],
            "Next_of_Kin_Emergency_Contact": {},
            "Health_Certificates_Vaccinations": [],
            "Covid_19_Vaccination": {},
            "Marine_Courses": [],
            "Sea_Service_Details": [],
            "Specialised_Experience": [],
            "References": [],
            "Declaration": {},
            "Office_Use_Only": {},
            "error": str(e)
        }
    
    # Ensure all expected keys exist with proper structure
    default_structure = {
        "Personal_Details": {},
        "Education": {},
        "Contact_Details": {},
        "Travel_Documents": [],  # Array
        "Professional_Qualifications": [],  # Array
        "Next_of_Kin_Emergency_Contact": {},
        "Health_Certificates_Vaccinations": [],  # Array
        "Covid_19_Vaccination": {},
        "Marine_Courses": [],  # Array
        "Sea_Service_Details": [],  # Array
        "Specialised_Experience": [],  # Array
        "References": [],  # Array
        "Declaration": {},
        "Office_Use_Only": {},
    }
    
    # Merge with defaults to ensure all keys exist
    for key, default_value in default_structure.items():
        if key not in result:
            result[key] = default_value
        # Convert empty objects to arrays where needed
        elif isinstance(default_value, list) and isinstance(result[key], dict) and not result[key]:
            result[key] = []
    
    print("=" * 80)
    print("FINAL STRUCTURED DATA:")
    print(json.dumps(result, indent=2)[:1000])
    print("=" * 80)

    result = normalize_for_serializer(result)
    return result
    
    
