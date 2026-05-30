import streamlit as st
import pandas as pd
import json
import time
import os
import requests
import google.generativeai as genai
import PyPDF2
import docx
from io import BytesIO

# --- AI Extraction Logic ---
def extract_text_from_pdf(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def extract_text_from_docx(docx_file):
    """Extract text from a DOCX file using python-docx."""
    doc = docx.Document(docx_file)
    text = ""
    for paragraph in doc.paragraphs:
        if paragraph.text.strip():
            text += paragraph.text + "\n"
    # Also extract text from tables (CVs often use tables for layout)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if cell.text.strip():
                    text += cell.text + "\n"
    return text

def parse_cv_with_ai(file_bytes, cv_text, api_key, target_rank="All Ranks", filename="", is_docx=False):
    genai.configure(api_key=api_key)
    model_name = None
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name or 'pro' in m.name:
                    model_name = m.name
                    break
    except Exception as e:
        return {"error": f"API Error (Likely invalid or expired API Key): {str(e)}"}
                
    if not model_name:
        return {"error": "No supported text generation models found for this API key."}
        
    model = genai.GenerativeModel(model_name)
    
    prompt = f"""
    You are an AI assistant that extracts structured information from resumes/CVs.
    
    Target Rank to look for: {target_rank}
    Filename (use as a hint if the CV text is incomplete): {filename}
    
    Extract the following details from the {'document text below' if is_docx else 'attached PDF document'}.
    - Full Name (IMPORTANT: If the name is not clearly found in the document, try to infer it from the filename above. The filename often contains the rank and full name, e.g. "OILER John Smith.pdf")
    - Email Address (IMPORTANT: Look for any email address. It may be labeled as "Email", "E-mail", "Gmail", "GMAIL", "Mail", "E-Mail Address", or similar. Extract the full email address like example@gmail.com)
    - Phone Number (may be labeled as "Phone", "Mobile", "Tel", "Mob", "Cell", "WhatsApp", or similar)
    - Rank (IMPORTANT: Infer the most recent rank from the document. If not found, infer from the filename. If the candidate's rank clearly matches or is equivalent to the Target Rank '{target_rank}', output exactly '{target_rank}'. Otherwise, output their actual inferred rank.)
    
    CRITICAL: Never return empty strings if you can infer the information from either the document OR the filename. Try your best to fill every field.
    
    Return ONLY a valid JSON object with the following exact keys:
    {{"full_name": "", "email": "", "phone": "", "rank": ""}}
    """
    
    try:
        if is_docx:
            # For DOCX files, send extracted text as part of the prompt
            docx_prompt = prompt + f"\n\n--- DOCUMENT TEXT ---\n{cv_text}\n--- END OF DOCUMENT ---"
            response = model.generate_content(docx_prompt)
        else:
            # For PDF files, send the raw binary directly to Gemini
            response = model.generate_content([
                {"mime_type": "application/pdf", "data": file_bytes},
                prompt
            ])
        text_resp = response.text.strip()
        
        if text_resp.startswith("```json"):
            text_resp = text_resp[7:]
        elif text_resp.startswith("```"):
            text_resp = text_resp[3:]
            
        if text_resp.endswith("```"):
            text_resp = text_resp[:-3]
            
        return json.loads(text_resp.strip())
    except Exception as e:
        return {"error": str(e)}

# --- Django Integration Logic ---
def send_to_django(extracted_data, file_obj, django_url, auth_token=""):
    """Send extracted data and PDF file to Django Backend via POST request."""
    # Reset file pointer to beginning so the requests library can read the PDF bytes
    file_obj.seek(0)
    
    # We send the data as multipart/form-data so we can include the physical file
    # Ensure the key 'file' matches what your Django serializer expects for the document!
    # Determine correct mime type based on file extension
    file_ext = os.path.splitext(file_obj.name)[1].lower()
    if file_ext == '.docx':
        mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    else:
        mime_type = 'application/pdf'
    
    files = {
        'file': (file_obj.name, file_obj, mime_type)
    }
    
    # The extracted JSON data is sent as form fields. 
    # Make sure these keys exactly match the fields in your Django model/serializer.
    data = {
        'name': extracted_data.get("full_name", ""),
        'email': extracted_data.get("email", ""),
        'phone': extracted_data.get("phone", ""),
        'position': extracted_data.get("rank", ""),
    }
    
    headers = {}
    if auth_token:
        # Adjust 'Bearer' to 'Token' or 'JWT' depending on your Django auth configuration
        headers['Authorization'] = f'Bearer {auth_token}'  
        
    try:
        response = requests.post(django_url, data=data, files=files, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (like 400 or 500)
        
        # Try to parse response JSON, but handle cases where Django returns empty body
        try:
            resp_data = response.json()
        except ValueError:
            resp_data = {"status": "Success, but no JSON returned"}
            
        return True, resp_data
    except requests.exceptions.RequestException as e:
        # Return the exact error string (and response body if available) to help debugging
        err_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            err_msg += f" | Body: {e.response.text}"
        return False, err_msg

# --- Streamlit UI ---
st.set_page_config(page_title="CV AI Extractor", page_icon="🤖", layout="wide")

st.title("🤖 AI-Powered CV Extractor (API Integrated)")
st.markdown("Upload PDFs to extract candidate data and push them directly to your Django backend (`/api/documents/`).")

# Sidebar for Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key", type="password", help="Required for AI extraction.")
    st.divider()
    st.subheader("Django Connection")
    django_url = st.text_input("Django API Endpoint", value="https://backend.sakrshipping.com/api/documents/")
    django_token = st.text_input("Django Auth Token (Optional)", type="password", help="If your API requires authentication.")

# Upload Area
st.subheader("📤 Upload Candidate CVs")

ranks = [
    "All Ranks", "Master / Captain", "Staff Captain", "Chief Officer / Chief Mate", "Second Officer",
    "Third Officer", "Dynamic Positioning Operator (DPO)", "ROV Supervisor",
    "Offshore Installation Manager", "Deck Cadet", "Bosun", "ABLE SEAFARER DECK",
    "Able Seaman (AB)", "Ordinary Seaman (OS)", "Carpenter", "Pumpman", "Crane Operator",
    "Water and Pool", "Security Guard", "Life Guard", "Upholsterer", "Doctor",
    "Hotel Director", "Assistant Hotel Director", "Purser", "Assistant Purser",
    "Food & Beverage Manager", "Executive Chef", "Chief Housekeeper", "Guest Services Manager",
    "Restaurant Manager", "Head Waiter", "Waiter", "F&B attendant", "Bartender",
    "Cabin Steward", "Laundryman", "Cook", "2nd Cook", "3rd Cook", "Assistant Cook",
    "Baker", "Assistant Baker", "Pastry", "Assistant pastry", "Butcher", "Steward",
    "Utility Galley", "Tour Expert", "Photographer", "Chief Engineer", "Second Engineer",
    "Third Engineer", "Fourth Engineer", "ETO", "2ND ETO", "3RD ETO", "ELECTRICAL ENGINEER",
    "Refrigeration Engineer", "HVAC Engineer", "Engine Cadet", "Gas Engineer",
    "Cargo Engineer", "Reliquefaction Engineer", "Motorman", "Mechanic", "Assistant Mechanic",
    "Oiler", "Wiper", "Fitter", "Welder", "Plumber", "Assistant Plumber", "Electrician",
    "2nd Electrician", "3rd Electrician", "Assistant Electrician", "Trainee Electrician",
    "AC Technician", "Senior Accommodation Repairman", "Junior Accommodation Repairman", "Other"
]
target_rank = st.selectbox("Filter by Target Rank", options=ranks)

uploaded_files = st.file_uploader("Drop PDF or DOCX files here", type=["pdf", "docx"], accept_multiple_files=True)

if uploaded_files:
    if not api_key:
        st.warning("⚠️ Please enter your Gemini API Key in the sidebar.")
    elif not django_url:
        st.warning("⚠️ Please enter the Django API URL in the sidebar.")
    else:
        if st.button("Extract & Send to Django", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            successful_uploads = []
            
            for i, file in enumerate(uploaded_files):
                status_text.text(f"Processing {file.name} ({i+1}/{len(uploaded_files)})...")
                
                # Step A: Read raw bytes and extract text
                file.seek(0)
                file_bytes = file.read()
                file.seek(0)
                
                file_ext = os.path.splitext(file.name)[1].lower()
                is_docx = file_ext == '.docx'
                
                if is_docx:
                    cv_text = extract_text_from_docx(file)
                else:
                    cv_text = extract_text_from_pdf(file)
                
                # Step B: AI Parse (PDF sent as binary, DOCX sent as extracted text)
                result = parse_cv_with_ai(file_bytes, cv_text, api_key, target_rank, filename=file.name, is_docx=is_docx)
                
                if "error" in result:
                    st.error(f"❌ Failed to parse {file.name}: {result['error']}")
                else:
                    import re
                    # Fallback: If AI couldn't extract the name, extract it from the filename
                    if not result.get("full_name"):
                        # Remove .pdf, numbers, and common suffixes
                        clean_name = re.sub(r'\.(pdf|docx)$', '', file.name, flags=re.IGNORECASE)
                        clean_name = re.sub(r'_Application|_CV|\d+', '', clean_name, flags=re.IGNORECASE)
                        clean_name = clean_name.replace('_', ' ').strip()
                        
                        # In files like "OILER Mahmoud", we try to separate rank and name, 
                        # but just setting the whole cleaned string ensures Django doesn't crash
                        result["full_name"] = clean_name
                        st.info(f"ℹ️ Name not found in text. Fallback extracted from filename: {clean_name}")

                    # Show what the AI extracted (for debugging)
                    with st.expander(f"🔍 AI Extraction Result for {file.name}"):
                        st.json(result)
                        if not result.get("email"):
                            st.warning("⚠️ No email found! Showing raw PDF text below:")
                            st.text_area("Raw PDF Text", cv_text[:3000], height=200)
                    
                    extracted_rank = result.get("rank", "Unknown")
                    if not extracted_rank or extracted_rank == "Unknown":
                        extracted_rank = target_rank if target_rank != "All Ranks" else "Unknown"
                        result["rank"] = extracted_rank
                    
                    if target_rank != "All Ranks" and extracted_rank.lower() != target_rank.lower():
                        st.warning(f"⏭️ Skipped {file.name}: Rank ({extracted_rank}) does not match target ({target_rank}).")
                    else:
                        # Step C: Send to Django
                        status_text.text(f"Sending {file.name} to Django API...")
                        success, api_response = send_to_django(result, file, django_url, django_token)
                        
                        if success:
                            st.success(f"✅ Successfully sent {file.name} to Django!")
                            successful_uploads.append({"filename": file.name, **result})
                        else:
                            st.error(f"❌ Django API Error for {file.name}: {api_response}")
                
                progress_bar.progress((i + 1) / len(uploaded_files))
                
                if i < len(uploaded_files) - 1:
                    status_text.text(f"Pausing 15s for Gemini API limits (File {i+1} of {len(uploaded_files)} done)...")
                    time.sleep(15)
            
            status_text.text("✅ All processing complete!")
            
            if successful_uploads:
                with st.expander("View Successfully Uploaded Data"):
                    st.json(successful_uploads)
