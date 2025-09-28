# #utils/document_to_json.py
# import json
# #from langchain.llms import Ollama
# #from langchain_community.llms import Ollama

# from langchain.prompts import PromptTemplate
# from langchain.output_parsers import StructuredOutputParser, ResponseSchema
# from langchain.chains import LLMChain
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


# def convert_text_to_json(extracted_text: str) -> dict:
#     """
#     Convert extracted document text into structured JSON using Ollama + StructuredOutputParser.
#     """

#     llm = OllamaLLM(model="llama3.2:1b")  # change to llama2, gemma, etc. if installed

#     prompt = PromptTemplate(
#         template="""
# You are an expert information extraction system.

# Extract structured data from the following CV text.

# Text:
# {document}

# Follow these instructions strictly:
# {format_instructions}
# """,
#         input_variables=["document"],
#         partial_variables={"format_instructions": format_instructions},
#     )

#     chain = LLMChain(llm=llm, prompt=prompt)
#     result = chain.run({"document": extracted_text})

#     try:
#         return output_parser.parse(result)
#     except Exception as e:
#         return {"error": str(e), "raw_output": result}








import json
import re
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_ollama import OllamaLLM

# 1. Define schema fields
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
]

# 2. Create the parser
output_parser = StructuredOutputParser.from_response_schemas(response_schemas)

# 3. Format instructions (JSON schema instructions)
format_instructions = output_parser.get_format_instructions()


def repair_json_string(text: str) -> str:
    """Try to fix common JSON formatting errors from LLM output."""
    
    # Handle different response types
    if hasattr(text, 'content'):
        text = text.content
    else:
        text = str(text)
    
    # Remove markdown code fences
    text = re.sub(r"^```json|```$", "", text.strip(), flags=re.MULTILINE)
    
    # Fix the specific issue: remove extra quotes around values like '"value"'
    text = re.sub(r"'\"([^\"]*?)\"'", r'"\1"', text)
    
    # Replace single quotes with double quotes for values
    text = re.sub(r":\s*'([^']*?)'", r': "\1"', text)
    
    # Fix standalone single quotes that should be double quotes
    text = re.sub(r"(?<!\\)'", '"', text)
    
    # Remove broken }: artifacts
    text = re.sub(r'"}:\s*', '", ', text)
    text = re.sub(r'"}\s*:', '", ', text)
    
    # Ensure keys are quoted (but don't double-quote already quoted keys)
    text = re.sub(r'(?<!")(\w+)(?=\s*:)', r'"\1"', text)
    
    # Fix arrays with mixed quotes - convert to proper JSON array
    # Handle cases like 'value1', 'value2' -> ["value1", "value2"]
    def fix_array_content(match):
        content = match.group(1)
        # Split by comma and clean each item
        items = [item.strip().strip("'\"") for item in content.split(',')]
        return '"' + ' | '.join(items) + '"'  # Join as single string for now
    
    # Apply array fixing to content between quotes
    text = re.sub(r'"([^"]*(?:\'[^\']*\'[^"]*)+)"', fix_array_content, text)
    
    # Collapse multiple commas
    text = re.sub(r',\s*,+', ',', text)
    
    # Replace ellipses with empty strings
    text = text.replace("...", '""')
    
    # Fix trailing commas before closing braces/brackets
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)
    
    # Remove any remaining single quotes that might cause issues
    text = re.sub(r"(?<![\w])'(?![\w])", '"', text)
    
    return text


def extract_json_data_manually(text: str) -> dict:
    """Manually extract data from malformed JSON when parsing fails."""
    result = {}
    
    # Define the expected keys
    expected_keys = [
        "Personal_Details", "Education", "Contact_Details", "Travel_Documents",
        "Professional_Qualifications", "Next_of_Kin_Emergency_Contact",
        "Health_Certificates_Vaccinations", "Covid_19_Vaccination", "Marine_Courses",
        "Sea_Service_Details", "Specialised_Experience", "References",
        "Declaration", "Office_Use_Only"
    ]
    
    for key in expected_keys:
        # Look for the pattern "key": 'value' or "key": "value"
        pattern = rf'"{key}":\s*[\'"]([^\'"]*)[\'"[^,}}]*'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            result[key] = match.group(1).strip()
        else:
            result[key] = ""
    
    return result


def convert_text_to_json(extracted_text: str) -> dict:
    """
    Convert extracted document text into structured JSON using Ollama + StructuredOutputParser.
    """

    llm = OllamaLLM(model="llama3.2:1b")  # change to llama2, gemma, etc. if installed

    prompt = PromptTemplate(
        template="""
You are an expert information extraction system.

Extract structured data from the following CV text.

Text:
{document}

IMPORTANT: Return ONLY valid JSON with double quotes for all strings. Example format:
{{
    "Personal_Details": "John Doe, Egyptian, Born 1990",
    "Education": "University degree",
    "Contact_Details": "email@example.com, +123456789"
}}

Do NOT use single quotes. Do NOT add extra quotes around values.
{format_instructions}
""",
        input_variables=["document"],
        partial_variables={"format_instructions": format_instructions},
    )

    # Updated syntax: Use pipe operator instead of LLMChain
    chain = prompt | llm
    raw_result = chain.invoke({"document": extracted_text})

    # Multiple parsing strategies
    parsing_strategies = [
        # Strategy 1: Try structured parser directly
        lambda x: output_parser.parse(x),
        # Strategy 2: Try JSON parsing after repair
        lambda x: json.loads(repair_json_string(x)),
        # Strategy 3: Manual extraction
        lambda x: extract_json_data_manually(repair_json_string(x)),
    ]

    for i, strategy in enumerate(parsing_strategies):
        try:
            result = strategy(raw_result)
            if isinstance(result, dict) and len(result) > 0:
                return result
        except Exception as e:
            if i == len(parsing_strategies) - 1:  # Last strategy
                return {
                    "error": f"All parsing strategies failed. Last error: {str(e)}", 
                    "raw_output": repair_json_string(raw_result)
                }
            continue

    return {"error": "No valid parsing strategy found", "raw_output": str(raw_result)}


# Alternative function with more aggressive JSON cleaning
def convert_text_to_json_robust(extracted_text: str) -> dict:
    """
    More robust version with additional JSON repair strategies.
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

Use empty strings "" for missing information.
""",
        input_variables=["document"],
    )

    chain = prompt | llm
    raw_result = chain.invoke({"document": extracted_text})
    
    # Multiple parsing attempts
    parsing_attempts = [
        lambda x: json.loads(x),
        lambda x: json.loads(repair_json_string(x)),
        lambda x: output_parser.parse(x),
    ]
    
    for attempt in parsing_attempts:
        try:
            result = attempt(raw_result)
            if isinstance(result, dict):
                return result
        except Exception:
            continue
    
    # Final fallback
    return {
        "error": "All parsing methods failed", 
        "raw_output": repair_json_string(raw_result)
    }
    