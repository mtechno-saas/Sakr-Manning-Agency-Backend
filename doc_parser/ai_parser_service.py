

# import json
# import yaml
# import docx2txt
# from langchain_community.document_loaders import PyPDFLoader, TextLoader
# from langchain_ollama.llms import OllamaLLM
# from langchain.prompts import PromptTemplate
# from langchain.chains import LLMChain
# import re


# def extract_document_features(file_path: str, model: str = "gemma3:1b") -> str:
#   """
#   Reads a document, extracts features using an Ollama model through LangChain,
#   and returns the result in YAML format.


#   Args:
#   file_path (str): Path to the input document.
#   model (str): Ollama model name (default: gemma3:1b).


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

#   IMPORTANT: Return ONLY valid YAML format. Do not include markdown code blocks, backticks, or any other formatting.
#   If a field is not found in the document, use null or an empty string.

#   Document:
#   {document}
#   """


#   prompt = PromptTemplate(template=template, input_variables=["document"])
#   chain = prompt | llm


#   # --- Step 4: Run extraction ---
#   response = chain.invoke({"document": text_content[:4000]}) # limit to 4k chars for safety

#   # --- Step 5: Clean the response ---
#   cleaned_response = _clean_yaml_response(response)

#   # --- Step 6: Validate YAML ---
#   try:
#     parsed_yaml = yaml.safe_load(cleaned_response)
#     return yaml.dump(parsed_yaml, sort_keys=False, allow_unicode=True, default_flow_style=False)
#   except yaml.YAMLError as e:
#     print(f"YAML parsing error: {e}")
#     print(f"Cleaned response: {cleaned_response}")
#     return cleaned_response


# def _clean_yaml_response(response: str) -> str:
#     """
#     Clean the AI response by removing markdown formatting and handling JSON responses.
#     """
#     if not response:
#         return ""
    
#     # Remove markdown code blocks
#     response = re.sub(r'```(?:yaml|json)?\s*\n?', '', response, flags=re.IGNORECASE)
#     response = re.sub(r'```\s*\n?', '', response)
    
#     # Remove leading/trailing whitespace
#     response = response.strip()
    
#     # Remove any leading backticks that might remain
#     response = re.sub(r'^`+', '', response)
#     #response = re.sub(r'`+, '', response)
    
#     # Check if the response is JSON format
#     try:
#         json_data = json.loads(response)
        
#         # Handle case where AI returns {"document": [array of objects]}
#         if isinstance(json_data, dict) and "document" in json_data:
#             document_data = json_data["document"]
#             if isinstance(document_data, list) and len(document_data) > 0:
#                 # Take the first object that has the most complete data
#                 best_record = _find_most_complete_record(document_data)
#                 # Convert JSON to YAML format
#                 return yaml.dump(best_record, default_flow_style=False, allow_unicode=True)
        
#         # Handle case where AI returns a single object or array directly
#         elif isinstance(json_data, list) and len(json_data) > 0:
#             best_record = _find_most_complete_record(json_data)
#             return yaml.dump(best_record, default_flow_style=False, allow_unicode=True)
        
#         elif isinstance(json_data, dict):
#             return yaml.dump(json_data, default_flow_style=False, allow_unicode=True)
            
#     except json.JSONDecodeError:
#         # Not JSON, try to process as YAML
#         pass
    
#     # If the response starts with non-YAML content, try to extract YAML part
#     lines = response.split('\n')
#     yaml_started = False
#     yaml_lines = []
    
#     for line in lines:
#         # Check if line looks like YAML (key: value format)
#         if ':' in line and not yaml_started:
#             yaml_started = True
        
#         if yaml_started:
#             yaml_lines.append(line)
    
#     if yaml_lines:
#         response = '\n'.join(yaml_lines)
    
#     return response.strip()


# def _find_most_complete_record(records):
#     """
#     Find the record with the most non-null/non-empty values from a list of records.
#     """
#     if not records or not isinstance(records, list):
#         return {}
    
#     best_record = records[0]
#     max_fields = 0
    
#     for record in records:
#         if not isinstance(record, dict):
#             continue
            
#         # Count non-null, non-empty fields
#         field_count = sum(1 for value in record.values() 
#                          if value is not None and str(value).strip() != "")
        
#         if field_count > max_fields:
#             max_fields = field_count
#             best_record = record
    
#     return best_record

"""
Fixed AI Parser Service that handles YAML parsing errors and deprecation warnings.
"""

import os
import re
import yaml
import logging
from typing import Dict, Any, Optional
from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

# Try to import docx2python, fall back to python-docx if not available
try:
    from docx2python import docx2python
    DOCX2PYTHON_AVAILABLE = True
except ImportError:
    DOCX2PYTHON_AVAILABLE = False
    try:
        from docx import Document
        PYTHON_DOCX_AVAILABLE = True
    except ImportError:
        PYTHON_DOCX_AVAILABLE = False

logger = logging.getLogger(__name__)


def extract_structured_content_from_docx(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract structured content from DOCX files using docx2python (preferred) or python-docx (fallback).
    
    Args:
        file_path (str): Path to the DOCX file
        
    Returns:
        Dict containing extracted text, tables, images, and properties, or None if extraction fails
    """
    try:
        if DOCX2PYTHON_AVAILABLE:
            return _extract_with_docx2python(file_path)
        elif PYTHON_DOCX_AVAILABLE:
            return _extract_with_python_docx(file_path)
        else:
            logger.error("No DOCX parsing library available. Install docx2python or python-docx.")
            return None
    except Exception as e:
        logger.error(f"Error extracting structured content from {file_path}: {str(e)}")
        return None


def _extract_with_docx2python(file_path: str) -> Dict[str, Any]:
    """Extract content using docx2python library."""
    docx_content = docx2python(file_path)
    
    # Extract text content
    text_content = docx_content.text
    
    # Extract tables
    tables = []
    if hasattr(docx_content, 'body') and docx_content.body:
        for table in docx_content.body:
            if isinstance(table, list) and len(table) > 0:
                # Clean up table data
                clean_table = []
                for row in table:
                    if isinstance(row, list):
                        clean_row = [str(cell).strip() for cell in row if str(cell).strip()]
                        if clean_row:  # Only add non-empty rows
                            clean_table.append(clean_row)
                if clean_table:
                    tables.append(clean_table)
    
    # Extract images
    images = []
    if hasattr(docx_content, 'images'):
        images = list(docx_content.images.keys()) if docx_content.images else []
    
    # Extract properties (fix deprecation warning)
    properties = {}
    if hasattr(docx_content, 'core_properties'):
        # Use core_properties instead of deprecated properties
        core_props = docx_content.core_properties
        if core_props:
            properties = {
                'title': getattr(core_props, 'title', ''),
                'subject': getattr(core_props, 'subject', ''),
                'creator': getattr(core_props, 'creator', ''),
                'keywords': getattr(core_props, 'keywords', ''),
                'description': getattr(core_props, 'description', ''),
                'last_modified_by': getattr(core_props, 'last_modified_by', ''),
                'revision': getattr(core_props, 'revision', ''),
                'created': str(getattr(core_props, 'created', '')),
                'modified': str(getattr(core_props, 'modified', '')),
                'category': getattr(core_props, 'category', ''),
            }
    elif hasattr(docx_content, 'properties'):
        # Fallback to deprecated properties with warning suppression
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", FutureWarning)
            properties = docx_content.properties or {}
    
    return {
        'text': text_content,
        'tables': tables,
        'images': images,
        'properties': properties,
        'extraction_method': 'docx2python'
    }


def _extract_with_python_docx(file_path: str) -> Dict[str, Any]:
    """Extract content using python-docx library (fallback)."""
    doc = Document(file_path)
    
    # Extract text from paragraphs
    text_parts = []
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text.strip())
    
    text_content = '\n'.join(text_parts)
    
    # Extract tables
    tables = []
    for table in doc.tables:
        table_data = []
        for row in table.rows:
            row_data = []
            for cell in row.cells:
                cell_text = cell.text.strip()
                if cell_text:
                    row_data.append(cell_text)
            if row_data:
                table_data.append(row_data)
        if table_data:
            tables.append(table_data)
    
    # Extract basic properties
    properties = {}
    if hasattr(doc, 'core_properties'):
        core_props = doc.core_properties
        properties = {
            'title': core_props.title or '',
            'subject': core_props.subject or '',
            'creator': core_props.author or '',
            'keywords': core_props.keywords or '',
            'description': core_props.comments or '',
            'created': str(core_props.created) if core_props.created else '',
            'modified': str(core_props.modified) if core_props.modified else '',
        }
    
    return {
        'text': text_content,
        'tables': tables,
        'images': [],  # python-docx doesn't easily extract image info
        'properties': properties,
        'extraction_method': 'python-docx'
    }


def prepare_enhanced_prompt_content(structured_data: Dict[str, Any]) -> str:
    """
    Prepare enhanced prompt content from structured document data.
    
    Args:
        structured_data: Dictionary containing extracted document content
        
    Returns:
        Formatted prompt content string
    """
    content_parts = []
    
    # Add document text
    if structured_data.get('text'):
        content_parts.append("=== DOCUMENT TEXT ===")
        content_parts.append(structured_data['text'])
        content_parts.append("")
    
    # Add tables
    if structured_data.get('tables'):
        content_parts.append("=== TABLES ===")
        for i, table in enumerate(structured_data['tables']):
            content_parts.append(f"Table {i+1}:")
            for row in table:
                content_parts.append(" | ".join(row))
            content_parts.append("")
    
    # Add document properties
    if structured_data.get('properties'):
        content_parts.append("=== DOCUMENT PROPERTIES ===")
        for key, value in structured_data['properties'].items():
            if value:
                content_parts.append(f"{key}: {value}")
        content_parts.append("")
    
    return "\n".join(content_parts)


def clean_yaml_response(response: str) -> str:
    """
    Clean the AI response to ensure valid YAML format.
    Handles markdown formatting and other common issues.
    
    Args:
        response (str): Raw response from the AI model
        
    Returns:
        Cleaned YAML string
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
    
    # Remove markdown bold formatting that breaks YAML
    response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
    response = re.sub(r'\*(.*?)\*', r'\1', response)
    
    # Remove markdown headers that break YAML
    response = re.sub(r'^#+\s*', '', response, flags=re.MULTILINE)
    
    # If the response contains explanatory text after YAML, remove it
    lines = response.split('\n')
    yaml_lines = []
    yaml_started = False
    
    for line in lines:
        line_stripped = line.strip()
        
        # Skip empty lines at the beginning
        if not yaml_started and not line_stripped:
            continue
            
        # Check if line looks like YAML (key: value format at start of line)
        if ':' in line and not yaml_started and not line_stripped.startswith(' '):
            yaml_started = True
        
        if yaml_started:
            # Stop if we encounter explanatory text that doesn't look like YAML
            if line_stripped and not line.startswith(' ') and ':' not in line and not line.endswith(':'):
                # Check if it's explanatory text (contains common words or patterns)
                explanatory_indicators = [
                    'note:', 'important:', 'please', 'the data', 'this document', 'based on',
                    'explanation', 'text here', 'some', 'qualifications', 'information'
                ]
                if any(indicator in line_stripped.lower() for indicator in explanatory_indicators):
                    break
                # Also break on standalone words that aren't YAML keys
                if len(line_stripped.split()) <= 3 and not line_stripped.endswith(':'):
                    break
            yaml_lines.append(line)
    
    if yaml_lines:
        response = '\n'.join(yaml_lines)
    
    return response.strip()


def validate_and_fix_yaml(yaml_content: str) -> str:
    """
    Validate YAML content and attempt to fix common issues.
    
    Args:
        yaml_content: YAML string to validate and fix
        
    Returns:
        Fixed YAML string
    """
    try:
        # Try to parse as-is first
        yaml.safe_load(yaml_content)
        return yaml_content
    except yaml.YAMLError as e:
        logger.warning(f"YAML validation failed: {e}")
        
        # Try common fixes
        fixed_content = yaml_content
        
        # Fix unquoted strings that contain special characters
        lines = fixed_content.split('\n')
        fixed_lines = []
        
        for line in lines:
            if ':' in line and not line.strip().startswith('#'):
                key, value = line.split(':', 1)
                value = value.strip()
                
                # Quote values that might cause issues
                if value and not (value.startswith('"') and value.endswith('"')):
                    # Check if value needs quoting
                    if any(char in value for char in ['*', '&', '!', '|', '>', "'", '"', '%', '@', '`']):
                        escaped_value = value.replace('"', '\\"')
                        value = f'"{escaped_value}"'
                        line = f"{key}: {value}"
                
            fixed_lines.append(line)
        
        fixed_content = '\n'.join(fixed_lines)
        
        try:
            yaml.safe_load(fixed_content)
            return fixed_content
        except yaml.YAMLError:
            logger.error("Could not fix YAML content")
            return yaml_content


def extract_data_from_document_enhanced(file_path: str) -> str:
    """
    Enhanced document data extraction using structured content analysis.
    
    Args:
        file_path (str): Path to the document file
        
    Returns:
        Extracted data in YAML format, or error message
    """
    try:
        # Step 1: Extract structured content
        structured_data = extract_structured_content_from_docx(file_path)
        if not structured_data:
            logger.error("Failed to extract structured content")
            return "Error: Could not extract structured content from document"
        
        # Step 2: Prepare enhanced prompt content
        enhanced_content = prepare_enhanced_prompt_content(structured_data)
        
        # Step 3: Process with AI using enhanced content
        ai_response = process_with_ai_enhanced(enhanced_content)
        
        if ai_response.startswith("Error:"):
            return ai_response
        
        # Step 4: Clean and validate YAML response
        cleaned_response = clean_yaml_response(ai_response)
        validated_response = validate_and_fix_yaml(cleaned_response)
        
        return validated_response
        
    except Exception as e:
        logger.error(f"Error in enhanced document extraction: {str(e)}")
        return f"Error: Enhanced extraction failed - {str(e)}"


def process_with_ai_enhanced(content: str) -> str:
    """
    Process document content with AI using enhanced structured prompting.
    
    Args:
        content (str): Enhanced document content with structure
        
    Returns:
        AI response with extracted data
    """
    try:
        # Initialize Ollama LLM
        llm = OllamaLLM(model="gemma3:1b")  # Using a more stable model
        
        # Enhanced prompt template
        prompt_template = PromptTemplate(
            input_variables=["content"],
            template="""
You are an expert at extracting seafarer information from documents. Extract the following information from the document content and return it in valid YAML format only.

IMPORTANT: 
- Return ONLY valid YAML, no explanations or markdown formatting
- Use "Not Available" for missing information
- Do not use asterisks (*) or other markdown formatting
- Ensure all values are properly quoted if they contain special characters

Extract these fields:

personal_information:
  full_name: ""
  date_of_birth: ""
  place_of_birth: ""
  nationality: ""
  passport_number: ""
  passport_issue_date: ""
  passport_expiry_date: ""
  seaman_book_number: ""
  seaman_book_issue_date: ""
  address: ""
  phone_number: ""
  email: ""

next_of_kin:
  full_name: ""
  relationship: ""
  address: ""
  phone_number: ""

medical_information:
  medical_certificate_number: ""
  medical_issue_date: ""
  medical_expiry_date: ""
  blood_type: ""

qualifications:
  highest_certificate_of_competency: ""
  issuing_country: ""
  issue_date: ""
  expiry_date: ""
  gmdss_certificate: ""
  gmdss_issue_date: ""
  gmdss_expiry_date: ""

experience:
  total_sea_service_months: ""
  last_vessel_name: ""
  last_vessel_type: ""
  last_rank: ""
  last_sign_off_date: ""

preferred_roles: []

availability_date: ""

Document content:
{content}

Return only the YAML data:"""
        )
        
        # Create the prompt
        prompt = prompt_template.format(content=content)
        
        # Get AI response
        response = llm.invoke(prompt)
        
        return response
        
    except Exception as e:
        logger.error(f"Error during AI processing: {e}")
        return "Error: AI processing failed"


# Backward compatibility function
def extract_data_from_document(file_path: str) -> str:
    """
    Backward compatibility wrapper for the enhanced extraction.
    
    Args:
        file_path (str): Path to the document file
        
    Returns:
        Extracted data in YAML format
    """
    return extract_data_from_document_enhanced(file_path)
