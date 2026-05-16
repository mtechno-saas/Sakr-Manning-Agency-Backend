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
# # format_instructions = output_parser.get_format_instructions()


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
# # format_instructions = output_parser.get_format_instructions()


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
# # format_instructions = output_parser.get_format_instructions()


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



"""
Pure Pydantic + Regex CV extraction engine.
No AI model required — extracts data instantly using pattern matching.
Output format matches the seafarer_application numbered-section API format.
"""

import re
from .schemas import (
    SeafarerApplication, PersonalDetails, MaritalStatus, Education,
    MarlineTest, LanguageLevel, ContactDetails, TravelDocument,
    ProfessionalQualification, NextOfKin, HealthSection, HealthCertificate,
    Covid19, MarineCourse, SeaServiceSection, ApplicantInfo, ServiceRecord,
    Reference, Declaration, DeclarationQuestions, DeclarationAnswer,
    OfficeUseOnly, ResponsiblePerson,
)


# ──────────────────────────────────────────────────────────────────────────────

CURRENT_TABLES = []

def _field(text: str, *labels: str, default: str = "") -> str:
    """
    Extract the value after the first matching label (case-insensitive).
    Handles multiple CV text layouts, including complex table rows.
    """
    global CURRENT_TABLES
    
    for label in labels:
        label_lower = label.lower()
        
        # 0. NATIVE TABLE PARSING (Option C)
        # Directly scan the 2D arrays extracted from python-docx to avoid flattened text regex issues.
        for table in CURRENT_TABLES:
            for r_idx, row in enumerate(table):
                for c_idx, cell in enumerate(row):
                    if label_lower in cell.lower():
                        # Case A: Vertical Table (Key | Value in the same row)
                        if c_idx + 1 < len(row) and row[c_idx + 1].strip():
                            val = row[c_idx + 1].strip()
                            if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val
                        
                        # Case B: Horizontal Table (Header row, Value row immediately below)
                        if r_idx + 1 < len(table) and c_idx < len(table[r_idx + 1]):
                            val = table[r_idx + 1][c_idx].strip()
                            if val and len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val
                            
        esc = re.escape(label)
        
        # 1. Colon/Dash separator (most common in typed CVs)
        m = re.search(rf"(?<!\w){esc}\s*[:\-]\s*(.+)", text, re.IGNORECASE)
        if m:
            val = m.group(1).split("\n")[0].strip()
            val = re.split(r"[ \t]{2,}", val)[0].strip()
            if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val

        # 2. Table Header Match (Same Line or Next Line)
        for line_match in re.finditer(rf"^(.*?{esc}.*)$", text, re.MULTILINE | re.IGNORECASE):
            line = line_match.group(1)
            idx = line.lower().find(label.lower())
            
            after_line_text = text[line_match.end():]
            m_next = re.match(r"[ \t]*\n([^\n]+)", after_line_text)
            
            headers = [(m.group(), m.start()) for m in re.finditer(r"[^\s]+(?: [^\s]+)*", line)]
            next_line = m_next.group(1) if m_next else ""
            values = [(m.group(), m.start()) for m in re.finditer(r"[^\s]+(?: [^\s]+)*", next_line)]
            
            # Is it a table row with multiple headers and values below?
            is_table = len(headers) > 1 and len(values) >= 1
            
            if is_table:
                for i, (h_text, h_pos) in enumerate(headers):
                    if label.lower() in h_text.lower():
                        # If python-docx flattened this table with pipe symbols, use exact column index matching!
                        if "|" in line and "|" in next_line:
                            pipe_headers = [h.strip() for h in line.split("|")]
                            pipe_values = [v.strip() for v in next_line.split("|")]
                            col_idx = -1
                            for c_i, ph in enumerate(pipe_headers):
                                if label.lower() in ph.lower():
                                    col_idx = c_i
                                    break
                            if col_idx != -1 and col_idx < len(pipe_values):
                                val = pipe_values[col_idx]
                                if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val
                                
                        # Otherwise, fallback to visual spatial alignment (for PDFs)
                        valid_values = [v for v in values if abs(v[1] - h_pos) <= 20]
                        if valid_values:
                            best_val = min(valid_values, key=lambda v: abs(v[1] - h_pos))
                            val = best_val[0]
                            if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val
                        break
            else:
                # Not a table, try same line separated by large spaces
                after_label = line[idx + len(label):]
                m_same = re.match(r"^[ \t]{2,}(.+)", after_label)
                if m_same:
                    val = m_same.group(1).strip()
                    val = re.split(r"[ \t]{2,}", val)[0].strip()
                    if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val
                    
                # Next line fallback
                if next_line:
                    val = next_line.strip()
                    val = re.split(r"[ \t]{2,}", val)[0].strip()
                    if len(val) > 1 and val.upper() not in [l.upper() for l in labels]: return val

    return default


def _email(text: str) -> str:
    m = re.search(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text)
    return m.group(0) if m else ""


def _phone(text: str) -> str:
    """Return the first phone number found."""
    patterns = [
        r"\+\d{1,3}[\s\-]?\d[\d\s\-]{6,15}",
        r"\b0\d{9,11}\b",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(0).strip()
    return ""


def _dates_near(text: str, keyword: str) -> tuple:
    """Return (iss_date, exp_date) found within 400 chars after keyword."""
    date_pat = r"(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{4}[/\-\.]\d{2}[/\-\.]\d{2})"
    m = re.search(re.escape(keyword), text, re.IGNORECASE)
    if not m:
        return ("", "")
    window = text[m.start(): m.start() + 400]
    dates = re.findall(date_pat, window)
    return (dates[0] if dates else "", dates[1] if len(dates) > 1 else "")


def _section(text: str, *headers: str, chars: int = 600) -> str:
    """Return text from the first matching section header onwards (limited chars)."""
    for h in headers:
        m = re.search(re.escape(h), text, re.IGNORECASE)
        if m:
            return text[m.start(): m.start() + chars]
    return ""


def _int_or_none(value: str):
    try:
        return int(re.sub(r"[^\d]", "", value)) if value else None
    except Exception:
        return None


# ──────────────────────────────────────────────────────────────────────────────
# SECTION EXTRACTORS
# ──────────────────────────────────────────────────────────────────────────────

def _extract_personal(text: str) -> PersonalDetails:
    # Marital Status: search for labels and then check for single/married keywords in the result
    ms_raw = _field(text, "Marital Status", "Marital_Status", "Status", "Marital").lower()
    
    # Fuzzy check: if the extracted value contains keywords, set the bools
    is_married = any(kw in ms_raw for kw in ["married", "widow", "divorce"])
    is_single = any(kw in ms_raw for kw in ["single", "unmarried", "bachelor"])
    
    # In some layouts, the [x] is what we look for. 
    # If the text is "[x] Single [ ] Married", both keywords exist. 
    # We need to check if [x] is closer to which one.
    if "[x]" in ms_raw or "[v]" in ms_raw or "✔" in ms_raw:
        # Very simple heuristic: which one has the marking closest to it
        m_idx = ms_raw.find("married")
        s_idx = ms_raw.find("single")
        x_idx = ms_raw.find("[x]") if "[x]" in ms_raw else ms_raw.find("✔")
        if x_idx != -1:
            if m_idx != -1 and abs(x_idx - m_idx) < abs(x_idx - s_idx if s_idx != -1 else 999):
                is_married = True
                is_single = False
            elif s_idx != -1:
                is_single = True
                is_married = False

    marital = MaritalStatus(single=is_single, married=is_married)
    
    # Height and Weight often have units in the label
    height_raw = _field(text, "Height", "Height (cm)", "Height_Cm", "HT", "Stature")
    weight_raw = _field(text, "Weight", "Weight (kg)", "Weight_Kg", "WT")
    
    # Name variations
    fn = _field(text, "Full Name", "Name", "Full_Name", "Surname", "First Name", "Givennames")
    
    return PersonalDetails(
        full_name=fn,
        date_of_birth=_field(text, "Date of Birth", "DOB", "Date_Of_Birth", "Birth Date", "Born"),
        marital_status=marital,
        nationality=_field(text, "Nationality", "Citizenship", "Country of Birth", "Country"),
        height_cm=_int_or_none(height_raw),
        weight_kg=_int_or_none(weight_raw),
        place_of_birth=_field(text, "Place of Birth", "Place_Of_Birth", "Birth Place", "Birthplace", "POB"),
        overall_size=_field(text, "Overall Size", "Coverall Size", "Overall_Size", "Size"),
        shirt_size=_field(text, "Shirt Size", "Shirt_Size", "Shirt"),
        nearest_port=_field(text, "Nearest Port", "Nearest_Port", "Port", "Home Port", "Airport", "Nearest Airport"),
        trouser_size=_field(text, "Trouser Size", "Trouser_Size", "Trouser", "Pants Size"),
        shoes_size=_field(text, "Shoes Size", "Shoe Size", "Shoes_Size", "Shoes", "Safety Shoes"),
    )


def _extract_education(text: str) -> Education:
    sec = _section(text, "Education", "EDUCATION", chars=1000)
    # Marlins test often has specific sub-headers from the template
    marlins_issued_by = _field(text, "Marlins Test Issued By", "Marlins Issued By")
    marlins_date = _field(text, "Marlins Test Date", "Marlins Date")
    marlins_result = _field(text, "Result %", "Result Percentage", "Marlins Result")
    marlins_at = _field(text, "Issued At", "Marlins Issued At", "Test Location")
    
    # English/German Language sections
    eng_sec = _section(text, "English Language", "English", chars=200)
    ger_sec = _section(text, "German Language", "German", chars=200)
    
    def get_lang_level(s: str) -> LanguageLevel:
        s = s.lower()
        # Look for [x], [X], [✔] or just X near the label
        return LanguageLevel(
            fluent="fluent" in s and re.search(r"fluent\s*\[[x✔]\]|\[[x✔]\]\s*fluent|fluent\s*[x✔]", s) is not None,
            good="good" in s and re.search(r"good\s*\[[x✔]\]|\[[x✔]\]\s*good|good\s*[x✔]", s) is not None,
            average="average" in s and re.search(r"average\s*\[[x✔]\]|\[[x✔]\]\s*average|average\s*[x✔]", s) is not None,
            poor="poor" in s and re.search(r"poor\s*\[[x✔]\]|\[[x✔]\]\s*poor|poor\s*[x✔]", s) is not None,
        )

    return Education(
        college_school=_field(text, "College / School", "College", "School", "Education"),
        marline_test=MarlineTest(
            issued_date=marlins_date,
            result_percentage=marlins_result,
            issued_by_authority=marlins_issued_by,
            issued_at=marlins_at,
        ),
        english_language=get_lang_level(eng_sec),
        german_language=get_lang_level(ger_sec),
    )


def _extract_contact(text: str) -> ContactDetails:
    return ContactDetails(
        home_address_city=_field(text, "Home Address", "Address", "Residence"),
        e_mail=_email(text) or _field(text, "Email", "E-mail"),
        mobile_tel=_phone(text) or _field(text, "Mobile / Tel", "Mobile", "Tel", "Phone"),
    )


def _extract_travel_docs(text: str) -> list:
    """Always returns Passport + Seaman Book + Other Seaman Book entries."""
    sec = _section(text, "Travel Documents", "TRAVEL DOCUMENTS", "4_travel", chars=1000)
    target = sec or text

    passport_no = _field(target, "Passport No", "Passport Number", "Passport #")
    p_iss, p_exp = _dates_near(target, "Passport")

    seaman_no = _field(target, "Seaman Book No", "Seaman Book Number", "Seaman's Book No")
    s_iss, s_exp = _dates_near(target, "Seaman Book")

    return [
        TravelDocument(
            type="Passport",
            document_no=passport_no,
            iss_date=p_iss or _field(target, "Passport Issue Date"),
            exp_date=p_exp or _field(target, "Passport Expiry Date"),
            iss_by_authority=_field(target, "Passport Issued By", "Passport Authority"),
            place_of_issue=_field(target, "Passport Place of Issue"),
        ),
        TravelDocument(
            type="Seaman Book",
            document_no=seaman_no,
            iss_date=s_iss or _field(target, "Seaman Book Issue Date"),
            exp_date=s_exp or _field(target, "Seaman Book Expiry Date"),
            iss_by_authority=_field(target, "Seaman Book Issued By"),
            place_of_issue=_field(target, "Seaman Book Place of Issue"),
        ),
        TravelDocument(type="Other Seaman Book"),
    ]


def _extract_qualifications(text: str) -> list:
    certs = []
    sec = _section(text, "Professional Qualification", "Certificate of Competency",
                   "5_professional", chars=1000)
    target = sec or text
    for cert_name, label in [("COC (Rank)", "COC"), ("GOC", "GOC")]:
        iss, exp = _dates_near(target, label)
        certs.append(ProfessionalQualification(
            certificate_name=cert_name,
            number=_field(target, f"{label} No", f"{label} Number"),
            issue_date=iss,
            expiry_date=exp,
            issued_by=_field(target, f"{label} Issued By", "Issued By"),
            issued_at=_field(target, f"{label} Issued At", "Issued At"),
        ))
    return certs


def _extract_next_of_kin(text: str) -> NextOfKin:
    sec = _section(text, "Next of Kin", "Emergency Contact", "6_next", chars=600)
    target = sec or text
    return NextOfKin(
        full_name=_field(target, "Full Name", "Name"),
        address_country=_field(target, "Address", "Country", "Address Country"),
        tel_no_mobile=_phone(target),
        relationship=_field(target, "Relationship", "Relation"),
        email=_email(target),
    )


def _extract_health(text: str) -> HealthSection:
    sec = _section(text, "Health Certificate", "Vaccinations", "7_health", chars=1200)
    target = sec or text

    certs = []
    for cert_type in ["International Medical", "Yellow Fever", "Cholera"]:
        m = re.search(re.escape(cert_type), target, re.IGNORECASE)
        if m:
            window = target[m.start(): m.start() + 300]
            iss, exp = _dates_near(window, cert_type[:5])
            certs.append(HealthCertificate(
                flag_state=cert_type,
                number=_field(window, "No", "Number", "#"),
                issue_date=iss,
                expiry_date=exp,
                issued_by=_field(window, "Issued By", "Authority"),
                issued_at=_field(window, "Issued At"),
            ))

    covid_sec = _section(text, "Covid", "COVID", "covid-19", chars=400)
    c_iss, c_2nd = _dates_near(covid_sec or text, "Covid") if covid_sec else ("", "")
    covid = Covid19(
        vaccination_name=_field(covid_sec or "", "Vaccine", "Vaccination Name"),
        first_dose=c_iss,
        second_dose=c_2nd,
    )

    return HealthSection(certificates=certs, covid_19=covid)


def _extract_marine_courses(text: str) -> list:
    sec = _section(text, "Marine Courses", "STCW", "8_marine", chars=3000)
    target = sec or text

    course_keywords = [
        "Crisis Management and Human Behavior",
        "Crowd Management",
        "Proficiency Of Security Awareness",
        "Security Awareness",
        "Elementary First Aid",
        "Fire Prevention and Fire Fighting",
        "Fire Fighting",
        "Passenger Safety Cargo Safety and Hull Integrity",
        "Personal Safety and Social Responsibilities",
        "Personal Survival Techniques",
        "Personal Survival",
        "Survival Craft",
        "Safety Training for Personal",
        "Advanced Fire Fighting",
        "Medical First Aid",
        "ECDIS", "GMDSS", "Radar", "ARPA",
        "Ship Security Officer", "SSO",
        "Basic Safety Training",
    ]

    courses = []
    seen = set()
    for kw in course_keywords:
        m = re.search(re.escape(kw), target, re.IGNORECASE)
        if m and kw not in seen:
            seen.add(kw)
            window = target[m.start(): m.start() + 350]
            iss, exp = _dates_near(window, kw[:6])
            courses.append(MarineCourse(
                course_name=kw,
                number=_field(window, "No", "Number", "Cert No", "Cert. No"),
                issue_date=iss,
                expiry_date=exp,
                issued_by_at=_field(window, "Issued By", "Issued At", "Authority"),
            ))
    return courses


def _extract_sea_service(text: str, applicant_name: str = "") -> SeaServiceSection:
    sec = _section(text, "Sea Service", "9_complete", "Service Details", chars=3000)
    target = sec or text

    rank_raw = _field(text, "Rank", "Position", "Applied Position")
    reg_code = _field(text, "Register Code", "Reg. Code", "Register_Code")

    info = ApplicantInfo(
        name=applicant_name,
        rank=rank_raw,
        register_code=reg_code,
    )

    records = []
    rank_keywords = [
        "Master", "Chief Officer", "Second Officer", "Third Officer",
        "Chief Engineer", "Second Engineer", "Third Engineer", "Fourth Engineer",
        "Electrician", "Bosun", "AB", "OS", "Cook", "Steward",
        "Captain", "Chief Mate", "Cadet", "Carpenter",
    ]
    date_pat = r"(\d{1,2}[/\-\.]\d{1,2}[/\-\.]\d{2,4}|\d{4}[/\-\.]\d{2}[/\-\.]\d{2})"
    seen_positions = set()

    for rank in rank_keywords:
        for m in re.finditer(r"\b" + re.escape(rank) + r"\b", target, re.IGNORECASE):
            window = target[max(0, m.start() - 100): m.start() + 500]
            dates = re.findall(date_pat, window)
            if len(dates) >= 2 and m.start() not in seen_positions:
                seen_positions.add(m.start())
                records.append(ServiceRecord(
                    company_name=_field(window, "Company", "Employer"),
                    rank=rank,
                    vessel_name_imo_number=_field(window, "Vessel", "Ship", "MV", "MT"),
                    flag=_field(window, "Flag"),
                    signed_on=dates[0],
                    signed_off=dates[1],
                    vessel_type=_field(window, "Vessel Type", "Ship Type", "Type"),
                    dwt_grt=_field(window, "DWT/GRT", "DWT", "GRT"),
                    engine_type=_field(window, "Engine Type", "Engine"),
                    bh_kw=_field(window, "BH/KW", "BHP", "KW"),
                    reason_for_sign_off=_field(window, "Reason", "Sign Off Reason"),
                ))

    return SeaServiceSection(applicant_info=info, service_records=records)


def _extract_references(text: str) -> list:
    sec = _section(text, "References", "10_references", chars=800)
    target = sec or ""
    refs = []
    if target:
        refs.append(Reference(
            no="1",
            company_management_country=_field(target, "Company", "Company/Management"),
            position=_field(target, "Position"),
            name=_field(target, "Name"),
            tel=_phone(target),
            email=_email(target),
        ))
    return refs


def _extract_declaration(text: str) -> Declaration:
    sec = _section(text, "Declaration", "11_declaration", chars=800)
    target = sec or text

    def yn(label) -> str:
        v = _field(target, label).upper()
        return "YES" if "YES" in v else "NO"

    return Declaration(
        questions=DeclarationQuestions(
            suffer_disease_unfit_for_sea=DeclarationAnswer(
                answer=yn("Disease"), details=""
            ),
            addicted_to_alcohol_or_drugs=DeclarationAnswer(answer=yn("Alcohol")),
            suffer_accident_disabled=DeclarationAnswer(answer=yn("Accident")),
            undergo_psychiatric_treatment=DeclarationAnswer(answer=yn("Psychiatric")),
        ),
        consent_statement=_field(target, "Consent", "I hereby declare"),
        place=_field(target, "Place"),
        date=_field(target, "Date"),
        signature=_field(target, "Signature"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# MAIN FUNCTION
# ──────────────────────────────────────────────────────────────────────────────

def convert_text_to_json(extracted_text: str, parsed_tables: list = None) -> dict:
    """
    Convert extracted CV text to structured data.
    First attempts LLM extraction (Option D) if OPENAI_API_KEY is configured.
    Falls back to native table parsing + regex (Option C).
    """
    global CURRENT_TABLES
    CURRENT_TABLES = parsed_tables or []
    
    text = extracted_text or ""

    # Maritime CV validation
    maritime_keywords = [
        'passport', 'seaman', 'coc', 'goc', 'rank', 'vessel', 'ship',
        'marine', 'maritime', 'stcw', 'certificate', 'sea service',
        'nationality', 'date of birth', 'personal details', 'marital status',
        'next of kin', 'emergency contact', 'vaccination', 'health certificate',
        'fire fighting', 'survival', 'sailor', 'officer', 'engineer',
        'captain', 'chief', 'deck', 'engine', 'flag state', 'imo',
        'dwt', 'grt', 'signed on', 'signed off', 'full name', 'port',
    ]
    text_lower = text.lower()
    keyword_count = sum(1 for kw in maritime_keywords if kw in text_lower)
    print(f"CV Validation: Found {keyword_count} maritime keywords, text length: {len(text.strip())}")

    if keyword_count < 5 or len(text.strip()) < 200:
        print("⚠️ DOCUMENT IS NOT A VALID MARITIME CV - RETURNING EMPTY DATA")
        return SeafarerApplication().to_numbered_dict()

    # ==========================================
    # OPTION D: LLM Local Extraction (Highest Accuracy)
    # ==========================================
    try:
        import os
        USE_LOCAL_LLM = os.environ.get("USE_LOCAL_LLM", "true").lower() == "true"
        
        if USE_LOCAL_LLM:
            print("🧠 Running LLM Extraction via Local Ollama (qwen2.5) (Option D)...")
            from langchain_ollama import ChatOllama
            
            # Using qwen2.5:latest for fast, free, and accurate structured extraction
            llm = ChatOllama(model="qwen2.5:latest", temperature=0)
            structured_llm = llm.with_structured_output(SeafarerApplication)
            
            prompt = f"Extract all relevant seafarer CV data from the following document.\n\nTEXT:\n{text}\n"
            if CURRENT_TABLES:
                prompt += f"\n\nNATIVE TABLES (Use this to match exact columns if text is confusing):\n{CURRENT_TABLES}"
            
            result = structured_llm.invoke(prompt)
            print("✅ LLM Extraction complete.")
            return result.to_numbered_dict()
    except Exception as e:
        print(f"⚠️ Local LLM extraction failed: {e}. Falling back to Native Table Parser (Option C)...")

    # ==========================================
    # OPTION C: Native Table + Regex Parser Fallback
    # ==========================================
    print("⚙️ Extracting data with Pydantic + Regex (Option C)...")


    print("✅ Extracting data with Pydantic + Regex (no AI model)...")

    personal = _extract_personal(text)
    applicant_name = personal.full_name or ""

    app = SeafarerApplication(
        **{
            "1_personal_details": personal,
            "2_education": _extract_education(text),
            "3_contact_details": _extract_contact(text),
            "4_travel_documents": _extract_travel_docs(text),
            "5_professional_qualification_certificate_of_competency": _extract_qualifications(text),
            "6_next_of_kin_emergency_contact": _extract_next_of_kin(text),
            "7_health_certificates_and_vaccinations": _extract_health(text),
            "8_marine_courses": _extract_marine_courses(text),
            "9_complete_sea_service_details": _extract_sea_service(text, applicant_name),
            "10_references": _extract_references(text),
            "11_declaration": _extract_declaration(text),
            "12_for_office_use_only": OfficeUseOnly(),
        }
    )

    result = app.to_numbered_dict()
    print(f"✅ Extraction complete. Applicant: {applicant_name or 'Unknown'}")
    return result
