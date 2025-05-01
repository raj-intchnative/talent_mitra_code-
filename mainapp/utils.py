import base64
import uuid
import os
from django.conf import settings

def save_base64_image(base64_str):
    """
    Saves a Base64-encoded image to the media/uploads folder.
    Returns the file path for the stored image.
    """
    try:
        image_data = base64.b64decode(base64_str)
        file_name = f"uploads/{uuid.uuid4()}.png"
        file_path = os.path.join(settings.MEDIA_ROOT, file_name)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(image_data)

        return f"/media/{file_name}"  # Relative URL for Django
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

import google.generativeai as genai
import PyPDF2
import docx
import json
import requests
import io
import pytesseract
from urllib.parse import urlparse, parse_qs
from pdf2image import convert_from_bytes
import logging


logging.basicConfig(level=logging.DEBUG)

# ✅ Configure Gemini AI with valid API key
genai.configure(api_key="AIzaSyA-1IUnyJorg6QJj-ftTJ2oLAWcutT6vDs")

pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

POPLER_PATH = r"C:\\Users\\rajen\\Downloads\\Release-24.08.0-0\\poppler-24.08.0\\Library\\bin"


def get_file_extension(file_url):
    """Extracts the file extension correctly from the GCS Signed URL."""
    parsed_url = urlparse(file_url)
    filename = parsed_url.path.split("/")[-1]  
    extension = filename.split(".")[-1].lower()  
    return extension


def fetch_file_from_url(file_url):
    """Fetch file content from a Signed URL and return binary content."""
    try:
        headers = {'Cache-Control': 'no-cache'}  
        response = requests.get(file_url, headers=headers, timeout=10)

        if response.status_code == 200:
            return io.BytesIO(response.content)
        else:
            raise Exception(f"Error fetching file: HTTP {response.status_code}")
    except Exception as e:
        raise Exception(f"Error fetching file: {str(e)}")


def extract_text_from_pdf(file_url):
    """Extract text from a PDF file, using OCR if necessary."""
    try:
        file_content = fetch_file_from_url(file_url)
        reader = PyPDF2.PdfReader(file_content)
        text = ""

        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text

        
        if not text.strip():
            file_content.seek(0)  # Reset file pointer to the beginning
            text = extract_text_with_ocr(file_content)

        return text.strip() if text.strip() else "Error: No readable text found in PDF."
    except Exception as e:
        return f"Error extracting text from PDF: {str(e)}"


def extract_text_with_ocr(file_content):
    """Extract text from scanned PDFs using OCR."""
    try:
        images = convert_from_bytes(file_content.read(), poppler_path=POPLER_PATH)
        ocr_text = " ".join([pytesseract.image_to_string(img) for img in images])
        return ocr_text.strip() if ocr_text.strip() else "Error: OCR could not extract text."
    except Exception as e:
        return f"Error performing OCR: {str(e)}"


def extract_text_from_docx(file_url):
    """Extract text from a DOCX file."""
    try:
        file_content = fetch_file_from_url(file_url)
        doc = docx.Document(file_content)
        return " ".join([para.text for para in doc.paragraphs])
    except Exception as e:
        return f"Error extracting text from DOCX: {str(e)}"


def extract_resume_data(file_url):
    """Extract structured data from a resume URL using Gemini AI."""
    try:
     
        file_extension = get_file_extension(file_url)

        if file_extension == "pdf":
            text = extract_text_from_pdf(file_url)
        elif file_extension == "docx":
            text = extract_text_from_docx(file_url)
        else:
            return "Error: Only PDF and DOCX files are accepted."

        # ✅ Handle errors in text extraction
        if "Error" in text:
            return text

        # ✅ Use Gemini AI to extract structured resume details
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(
            f"""
            Extract structured resume details in **valid JSON format only**.
            **Strictly return JSON without explanations, markdown, or formatting.**
            
            {{
              "name": "John Doe",
              "email": "johndoe@example.com",
              "contact": {{"mobile": "1234567890", "phone": "9876543210"}},
              "location": "New York",
              "education": [
                {{"institution": "University Name", "degree": "B.Tech in Computer Science",
                  "start_date": "August 2020", "end_date": "May 2024", "GPA": 8.5}}
              ],
              "experience": [
                {{"company": "Google", "role": "Software Engineer",
                  "start_date": "July 2022", "end_date": "Present",
                  "responsibilities": ["Developed AI models", "Worked on cloud deployment"]}}
              ],
              "skills": {{"Languages": ["Python", "C++", "JavaScript"],
                "Frameworks": ["Django", "Flask"],
                "Databases": ["MySQL", "MongoDB"]}},
              "total_experience": {{"years": 2, "months": 5}},
              "profile_summary": "Summarize the candidate's profile in 3-4 sentences based on education, experience, and skills."
            }}

            Resume Text:
            {text}
            """
        )

        
        print("\n🔍 AI Raw Response:", response.text)

        cleaned_response = response.text.strip().strip("```json").strip("```").strip()

        try:
            extracted_data = json.loads(cleaned_response)
            print(extracted_data)
            return extracted_data
        except json.JSONDecodeError:
            print("❌ Error: AI response is not in valid JSON format.")
            return None 

    except Exception as e:
        return f"Error processing resume: {str(e)}"


def save_extracted_data(extracted_data):
    """Save structured extracted data into the database."""

    try:
        
        name = extracted_data.get("name", "Unknown")
        email = extracted_data.get("email", None)
        contact = extracted_data.get("contact", {})
        mobile_number = contact.get("mobile", "")
        phone_number = contact.get("phone", "")
        location = extracted_data.get("location", "N/A")
        profile_summary = extracted_data.get("profile_summary", "")

        if not email:
            return "Error: Email is required to save candidate data."

        # ✅ Create or update Candidate entry
        candidate, _ = Candidate.objects.update_or_create(
            email=email,
            defaults={
                "name": name,
                "mobile_number": mobile_number,
                "phone_number": phone_number,
                "location": location,
                "profile_summary": profile_summary, 
            }
        )

        # ✅ Save Education Details
        CandidateEducation.objects.filter(candidate=candidate).delete()  
        for edu in extracted_data.get("education", []):
            CandidateEducation.objects.create(
                candidate=candidate,
                institution=edu.get("institution", "Unknown"),
                degree=edu.get("degree", "Unknown"),
                start_date=edu.get("start_date", ""),
                end_date=edu.get("end_date", ""),
                gpa=edu.get("GPA", 0.0)
            )

        # ✅ Save Work Experience
        CandidateExperience.objects.filter(candidate=candidate).delete()  
        for exp in extracted_data.get("experience", []):
            CandidateExperience.objects.create(
                candidate=candidate,
                company=exp.get("company", "Unknown"),
                role=exp.get("role", "Unknown"),
                start_date=exp.get("start_date", ""),
                end_date=exp.get("end_date", ""),
                responsibilities="\n".join(exp.get("responsibilities", []))
            )

        # ✅ Save Skills
        CandidateSkill.objects.filter(candidate=candidate).delete()  
        for skill_type, skills in extracted_data.get("skills", {}).items():
            for skill in skills:
                CandidateSkill.objects.get_or_create(
                    candidate=candidate, skill_type=skill_type, skill_name=skill
                )

        # ✅ Save Total Experience
        CandidateTotalExperience.objects.update_or_create(
            candidate=candidate,
            defaults={
                "total_years": extracted_data.get("total_experience", {}).get("years", 0),
                "total_months": extracted_data.get("total_experience", {}).get("months", 0)
            }
        )

        return f"✅ Candidate {candidate.name} data saved successfully."

    except Exception as e:
        return f"❌ Error saving extracted data: {str(e)}"



import re
from datetime import datetime

def calculate_total_experience(experience_list):
    """
    Calculates total experience in years from a list of experience entries.
    Each entry should be a dictionary with 'start_date' and optional 'end_date'.
    """
    total_months = 0
    for exp in experience_list:
        try:
            start_date = datetime.strptime(exp.get("start_date", ""), "%Y-%m-%d")
            end_date_str = exp.get("end_date") or datetime.now().strftime("%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
            total_months += (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        except:
            continue
    return total_months // 12

def extract_filter_criteria_using_custom_parser(user_input):
    """
    Extracts search filters like role, location, experience, skills, and education from user input.
    Returns a dictionary with keys: role, location, min_experience_years, skills, education.
    """

    filters = {
        "skills": None,
        "education": None,
        "role": None,
        "location": None,
        "min_experience_years": None
    }

    # --- Role Matching ---
    role_keywords = [
        "Full Stack Developer", "Frontend Developer", "Backend Developer",
        "Data Scientist", "Software Engineer", "Internship", "Intern", "DevOps Engineer"
    ]
    for role in role_keywords:
        if role.lower() in user_input.lower():
            filters["role"] = role
            break

    # Extract location: "in Noida", "at Bangalore"
    location_match = re.search(r"(?:in|at)\s+([A-Z][a-z]+(?:\s[A-Z][a-z]+)?)", user_input)
    if location_match:
        filters["location"] = location_match.group(1)
    else:
        # Fallback: single capitalized location word (e.g., "Noida")
        capitalized_words = re.findall(r"\b[A-Z][a-z]+\b", user_input)
        if capitalized_words:
            filters["location"] = capitalized_words[0]

    # Extract experience like "3+ years", "1-2 years", "5 years"
    exp_match = re.search(r"(\d+)(?:\s*[-+]\s*(\d+))?\s*years?", user_input)
    if exp_match:
        filters["min_experience_years"] = float(exp_match.group(1))

    # --- Skills (basic keywords match) ---
    skill_keywords = ["Python", "Java", "JavaScript", "React", "Django", "SQL", "Machine Learning", "AWS"]
    found_skills = [skill for skill in skill_keywords if skill.lower() in user_input.lower()]
    if found_skills:
        filters["skills"] = found_skills

    # --- Education Matching ---
    education_keywords = ["B.Tech", "B.E", "M.Tech", "MCA", "Bachelor", "Master", "PhD"]
    for edu in education_keywords:
        if edu.lower() in user_input.lower():
            filters["education"] = edu
            break

    return filters

# Example usage
if __name__ == "__main__":
    sample_input = "Looking for a Full Stack Developer Internship in Bangalore with 1-2 years of experience. Must know Python, React. Education: B.Tech"
    parsed_filters = extract_filter_criteria_using_custom_parser(sample_input)
    print("✅ Filters Extracted:", parsed_filters)


