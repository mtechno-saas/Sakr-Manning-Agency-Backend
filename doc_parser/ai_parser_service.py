# import yaml
# import docx2txt
# from langchain_community.document_loaders import PyPDFLoader, TextLoader
# from langchain_ollama.llms import OllamaLLM
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain


# def extract_document_features(file_path: str, model: str = "gemma3:1b") -> str:
#   """
#   Reads a document, extracts features using an Ollama model through LangChain,
#   and returns the result in YAML format.


#   Args:
#   file_path (str): Path to the input document.
#   model (str): Ollama model name (default: llama2).


#   Returns:
#   str: Extracted features in YAML format.
#   """


#   # --- Step 1: Load the document ---
#   text_content = ""
#   if file_path.endswith(".pdf"):
#     loader = PyPDFLoader(file_path)
#     documents = loader.load()
#     text_content = "\n".join([doc.page_content for doc in documents])
#   elif file_path.endswith(".docx"):
#     try:
#       text_content = docx2txt.process(file_path)
#     except Exception as e:
#       print(f"Error processing docx file with docx2txt: {e}")
#       return None
#   elif file_path.endswith(".txt"):
#     loader = TextLoader(file_path)
#     documents = loader.load()
#     text_content = "\n".join([doc.page_content for doc in documents])
#   else:
#     raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")

#   if not text_content:
#       return None

#   # --- Step 2: Initialize Ollama LLM ---
#   llm = OllamaLLM(model=model)


#   # --- Step 3: Define extraction prompt ---
#   template = """
#   You are an AI assistant. Extract structured features from the following document.
#   Features include:
#        full_name: string
#        date_of_birth: YYYY-MM-DD
#        place_of_birth: string
#        nationality: string
#        passport_number: string
#        passport_issue_date: YYYY-MM-DD
#        passport_expiry_date: YYYY-MM-DD
#        seaman_book_number: string
#        seaman_book_issue_date: YYYY-MM-DD
#        seaman_book_expiry_date: YYYY-MM-DD
#        address: string
#        phone_number: string
#        email: string


#   Return ONLY valid YAML.


#   Document:
#   {document}
#   """


#   prompt = PromptTemplate(template=template, input_variables=["document"])
#   chain = prompt | llm


#   # --- Step 4: Run extraction ---
#   response = chain.invoke({"document": text_content[:4000]}) # limit to 4k chars for safety


#   # --- Step 5: Validate YAML ---
#   try:
#     parsed_yaml = yaml.safe_load(response)
#     return yaml.dump(parsed_yaml, sort_keys=False, allow_unicode=True, default_flow_style=False)
#   except yaml.YAMLError:
#     return response

import json
import yaml
import docx2txt
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import re


def extract_document_features(file_path: str, model: str = "gemma3:1b") -> str:
  """
  Reads a document, extracts features using an Ollama model through LangChain,
  and returns the result in YAML format.


  Args:
  file_path (str): Path to the input document.
  model (str): Ollama model name (default: gemma3:1b).


  Returns:
  str: Extracted features in YAML format.
  """


  # --- Step 1: Load the document ---
  text_content = ""
  if file_path.endswith(".pdf"):
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_content = "\n".join([doc.page_content for doc in documents])
  elif file_path.endswith(".docx"):
    try:
      text_content = docx2txt.process(file_path)
    except Exception as e:
      print(f"Error processing docx file with docx2txt: {e}")
      return None
  elif file_path.endswith(".txt"):
    loader = TextLoader(file_path)
    documents = loader.load()
    text_content = "\n".join([doc.page_content for doc in documents])
  else:
    raise ValueError("Unsupported file type. Use PDF, DOCX, or TXT.")

  if not text_content:
      return None

  # --- Step 2: Initialize Ollama LLM ---
  llm = OllamaLLM(model=model)


  # --- Step 3: Define extraction prompt ---
  template = """
  You are an AI assistant. Extract structured features from the following document.
  Features include:
       full_name: string
       date_of_birth: YYYY-MM-DD
       place_of_birth: string
       nationality: string
       passport_number: string
       passport_issue_date: YYYY-MM-DD
       passport_expiry_date: YYYY-MM-DD
       seaman_book_number: string
       seaman_book_issue_date: YYYY-MM-DD
       seaman_book_expiry_date: YYYY-MM-DD
       address: string
       phone_number: string
       email: string

  IMPORTANT: Return ONLY valid YAML format. Do not include markdown code blocks, backticks, or any other formatting.
  If a field is not found in the document, use null or an empty string.

  Document:
  {document}
  """


  prompt = PromptTemplate(template=template, input_variables=["document"])
  chain = prompt | llm


  # --- Step 4: Run extraction ---
  response = chain.invoke({"document": text_content[:4000]}) # limit to 4k chars for safety

  # --- Step 5: Clean the response ---
  cleaned_response = _clean_yaml_response(response)

  # --- Step 6: Validate YAML ---
  try:
    parsed_yaml = yaml.safe_load(cleaned_response)
    return yaml.dump(parsed_yaml, sort_keys=False, allow_unicode=True, default_flow_style=False)
  except yaml.YAMLError as e:
    print(f"YAML parsing error: {e}")
    print(f"Cleaned response: {cleaned_response}")
    return cleaned_response


def _clean_yaml_response(response: str) -> str:
    """
    Clean the AI response by removing markdown formatting and handling JSON responses.
    """
    if not response:
        return ""
    
    # Remove markdown code blocks
    response = re.sub(r'```(?:yaml|json)?\s*\n?', '', response, flags=re.IGNORECASE)
    response = re.sub(r'```\s*\n?', '', response)
    
    # Remove leading/trailing whitespace
    response = response.strip()
    
    # Remove any leading backticks that might remain
    response = re.sub(r'^`+', '', response)
    #response = re.sub(r'`+, '', response)
    
    # Check if the response is JSON format
    try:
        json_data = json.loads(response)
        
        # Handle case where AI returns {"document": [array of objects]}
        if isinstance(json_data, dict) and "document" in json_data:
            document_data = json_data["document"]
            if isinstance(document_data, list) and len(document_data) > 0:
                # Take the first object that has the most complete data
                best_record = _find_most_complete_record(document_data)
                # Convert JSON to YAML format
                return yaml.dump(best_record, default_flow_style=False, allow_unicode=True)
        
        # Handle case where AI returns a single object or array directly
        elif isinstance(json_data, list) and len(json_data) > 0:
            best_record = _find_most_complete_record(json_data)
            return yaml.dump(best_record, default_flow_style=False, allow_unicode=True)
        
        elif isinstance(json_data, dict):
            return yaml.dump(json_data, default_flow_style=False, allow_unicode=True)
            
    except json.JSONDecodeError:
        # Not JSON, try to process as YAML
        pass
    
    # If the response starts with non-YAML content, try to extract YAML part
    lines = response.split('\n')
    yaml_started = False
    yaml_lines = []
    
    for line in lines:
        # Check if line looks like YAML (key: value format)
        if ':' in line and not yaml_started:
            yaml_started = True
        
        if yaml_started:
            yaml_lines.append(line)
    
    if yaml_lines:
        response = '\n'.join(yaml_lines)
    
    return response.strip()


def _find_most_complete_record(records):
    """
    Find the record with the most non-null/non-empty values from a list of records.
    """
    if not records or not isinstance(records, list):
        return {}
    
    best_record = records[0]
    max_fields = 0
    
    for record in records:
        if not isinstance(record, dict):
            continue
            
        # Count non-null, non-empty fields
        field_count = sum(1 for value in record.values() 
                         if value is not None and str(value).strip() != "")
        
        if field_count > max_fields:
            max_fields = field_count
            best_record = record
    
    return best_record