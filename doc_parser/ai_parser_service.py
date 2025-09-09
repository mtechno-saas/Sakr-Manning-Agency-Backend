# doc_parser/ai_parser_service.py
import docx
from langchain_ollama import OllamaLLM as Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

# The read_docx_text() and get_yaml_template() functions do not need to change.
# They are working perfectly.
def read_docx_text(file_path):
  """Reads text content from a .docx file."""
  try:
      doc = docx.Document(file_path)
      full_text = [para.text for para in doc.paragraphs]
      return '\n'.join(full_text)
  except Exception as e:
      print(f"Error reading docx file: {e}")
      return None

def get_yaml_template():
  """Returns the required YAML structure as a string."""
  # ... (This function is correct, no changes needed)
  return """Personal_Details:
Full_Name: ""
Date_Of_Birth: ""
Place_Of_Birth: ""
Nationality: ""
Marital_Status: ""
Height_Cm: ""
Weight_Kg: ""
Overall_Size: ""
Shirt_Size: ""
Trouser_Size: ""
Shoes_Size: ""
Nearest_Port: ""
Expected_Salary: ""
Available_Date: ""
Register_Code: ""


"""


def extract_data_from_document(document_text):
  """
  Uses LangChain and Ollama to extract structured data from document text.
  """
  # --- PROMPT UPDATE ---
  # This new prompt structure is more direct and less likely to elicit a chatty response.
  prompt_text = """You are an automated data extraction service. Your only function is to analyze the user's document text and fill in the provided YAML template with the extracted information.
Follow all rules precisely. Do not add any conversational text, apologies, or explanations. Only output the completed YAML.

*CRITICAL REQUIREMENTS:*
1. Extract values for ALL fields listed in the YAML structure.
2. Maintain the exact YAML hierarchy.
3. For list-type fields (indicated by -), create separate entries for each instance.
4. Use empty strings ("") for missing/unavailable values.
5. Format dates as YYYY-MM-DD when possible; if not, use the original format.
6. For percentage values, include only numbers (e.g., 85 not 85%).
7. For language fluency, use exact terms: "Fluent", "Good", "Average", or "Poor".
8. For health questions, use "Yes" or "No" answers.
9. Preserve original capitalization for names and places.
10. Combine address fields when appropriate.
11. Extract register codes exactly as they appear.
12. For Marine Courses, extract the Course_Name value exactly as it appears.

*DOCUMENT TEXT TO ANALYZE:*
---
{document_text}
---

*YAML TEMPLATE TO FILL:*
```yaml
{yaml_template}
COMPLETED YAML:
"""
  prompt = PromptTemplate.from_template(prompt_text)
  # I recommend trying phi3:mini as it's better at following instructions than gemma:2b
  llm = Ollama(model="phi3:3.8b-mini-4k-instruct-q4_0") 

  chain = prompt | llm | StrOutputParser()

  response = chain.invoke({
    "yaml_template": get_yaml_template(),
    "document_text": document_text
  })

  return response
