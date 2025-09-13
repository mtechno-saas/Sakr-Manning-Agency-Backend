import yaml
import docx2txt
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain


def extract_document_features(file_path: str, model: str = "gemma3:1b") -> str:
  """
  Reads a document, extracts features using an Ollama model through LangChain,
  and returns the result in YAML format.


  Args:
  file_path (str): Path to the input document.
  model (str): Ollama model name (default: llama2).


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


  Return ONLY valid YAML.


  Document:
  {document}
  """


  prompt = PromptTemplate(template=template, input_variables=["document"])
  chain = prompt | llm


  # --- Step 4: Run extraction ---
  response = chain.invoke({"document": text_content[:4000]}) # limit to 4k chars for safety


  # --- Step 5: Validate YAML ---
  try:
    parsed_yaml = yaml.safe_load(response)
    return yaml.dump(parsed_yaml, sort_keys=False, allow_unicode=True, default_flow_style=False)
  except yaml.YAMLError:
    return response
