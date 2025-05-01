
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
import os
import json
import uuid
import html
import pytz
from django.utils import timezone
from django.utils.timezone import now
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import CreateEmailTemplate, EmailLog, EmailTag ,Resume
from .serializers import CreateEmailTemplateSerializer, EmailFormSerializer, EmailTagSerializer
# from .forms import ResumeUploadForm
from .utils import extract_resume_data
from django.shortcuts import render

ist = pytz.timezone("Asia/Kolkata")  
kolkata_time = now().astimezone(ist)  

from django.conf import settings  # ✅ Import settings
from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import uuid
from .gcloud import GoogleCloudMediaFileStorage  

@csrf_exempt
def quill_upload(request):
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]
        
        # Generate a unique filename
        filename = f"uploads/{uuid.uuid4()}_{image.name}"

        # Use Google Cloud Storage to save the file
        storage = GoogleCloudMediaFileStorage()
        file_path = storage.save(filename, image)

        # ✅ Use settings.GS_BUCKET_NAME instead of undefined GS_BUCKET_NAME
        file_url = f"https://storage.googleapis.com/{settings.GS_BUCKET_NAME_IMG}/{file_path}"
        print(file_url)
        return JsonResponse({"url": file_url})

    return JsonResponse({"error": "No image uploaded"}, status=400)



def resize_image(image):
    img = Image.open(image)
    img.thumbnail((800, 800))  # Resize to max 800x800
    output = io.BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    
    return output  # Return resized image file object



@api_view(['POST'])
def create_email_template(request):
    serializer = CreateEmailTemplateSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_email_tags(request):
    tags = EmailTag.objects.values_list("name", flat=True)
    return Response({"tags": list(tags)})

@api_view(["GET"])
def email_types_api(request):
    email_types = CreateEmailTemplate.objects.filter(BoActive=True).values(
        "Email_Template_Id", "Email_Template_Description"
    )
    return Response(email_types, status=status.HTTP_200_OK)

def parse_parameters(param_string):
    params = {}

    for pair in param_string.split("$$"):
        print(f"Processing pair: {pair}")
        if "|" in pair:
            key, value = pair.split("|")
            params[key] = value
        else:
            raise ValueError(f"Invalid parameter format: {pair}")

    return params

@api_view(["POST"])
def send_email_api(request):
    serializer = EmailFormSerializer(data=request.data)
    if serializer.is_valid():
        email_from = serializer.validated_data["Email_From"]
        email_to = serializer.validated_data["Email_To"]
        email_type_id = serializer.validated_data["Email_Type"]
        param_string = serializer.validated_data["Parameters"]

        try:
            # Check if the email type exists
            email_record = CreateEmailTemplate.objects.get(Email_Template_Id=email_type_id, BoActive=True)
            subject = email_record.Email_Template_Subject
            body = email_record.Body_Html

            # Decode and replace parameters in email body
            body = html.unescape(body)
        
            parameters = parse_parameters(param_string)
            for key, value in parameters.items():
                placeholder = f"<<{key}>>"
                body = body.replace(placeholder, value)

            full_email_body = f"{body}"

            # Send email logic
            send_mail(
                subject=subject,
                message=body,  
                from_email=email_from,
                recipient_list=[email_to],
                html_message=full_email_body,
                fail_silently=False,
            )
         
            # Log success
            EmailLog.objects.create(
                email_template=email_record,
                user_type="Admin",  # Replace with dynamic user type if applicable
                email_to=email_to,
                email_subject=subject,
                email_body=full_email_body,
                email_send_date=kolkata_time,
                email_deliver_status="Delivered",
            )

            return Response(
                {"message": "Email sent successfully."}, status=status.HTTP_200_OK
            )

        except CreateEmailTemplate.DoesNotExist:
            return Response(
                {"error": "Invalid email type."}, status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            # Log failure
            EmailLog.objects.create(
                email_template=email_record if "email_record" in locals() else None,
                user_type="Admin",
                email_to=email_to,
                email_subject=subject if "subject" in locals() else "Unknown",
                email_body=body if "body" in locals() else "Unknown",
                email_deliver_status="Failed",
                email_failure_message=str(e),
            )
            return Response(
                {"error": f"Failed to send email: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.http import JsonResponse



# from .utils import extract_resume_data
# from .serializers import ResumeSerializer
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.parsers import MultiPartParser
# from rest_framework import status
# from google.cloud import storage
# from django.conf import settings
# from .models import Resume
# import logging
# import uuid
# import os
# from datetime import timedelta
# import json

# from .decorators import with_token_info 

# logger = logging.getLogger(__name__)

# class UploadResumeView(APIView):
#     parser_classes = [MultiPartParser]

#     def generate_unique_filename(self, original_filename):
#         name, ext = os.path.splitext(original_filename)
#         safe_name = f"{name.replace(' ', '_')}_{uuid.uuid4().hex}{ext}"
#         return safe_name

#     def upload_to_gcs(self, file_obj, unique_filename):
#         try:
#             client = storage.Client()
#             bucket = client.bucket(settings.GS_BUCKET_NAME)
#             blob = bucket.blob(f"{settings.GS_LOCATION}/{unique_filename}")
#             blob.upload_from_file(file_obj)

#             signed_url = blob.generate_signed_url(
#                 expiration=timedelta(minutes=60),
#                 method="GET"
#             )
#             return signed_url

#         except Exception as e:
#             logger.error(f"GCS Upload Failed: {e}")
#             return None

#     # @with_token_info  
#     def post(self, request, *args, **kwargs):
#         logger.info(f"Received request with files: {request.FILES}")

#         files = request.FILES.getlist("file")
#         if not files:
#             return Response({"error": "No files uploaded"}, status=status.HTTP_400_BAD_REQUEST)
#         user_id = request.data.get("user_id")
#         user_type = request.data.get("user_type")
#         if not user_id or not user_type:
#             return Response({"error": "Missing user_id or user_type"}, status=status.HTTP_400_BAD_REQUEST)

#         uploaded_files = []
#         for file_obj in files:
#             unique_filename = self.generate_unique_filename(file_obj.name)
#             signed_url = self.upload_to_gcs(file_obj, unique_filename)

#             if not signed_url:
#                 return Response({"error": f"Failed to upload {file_obj.name}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#             try:
#                 resume = Resume.objects.create(
#                     file_url=signed_url,
#                     uploaded_by_id=user_id,
#                     user_type=user_type
#                 )

#                 uploaded_files.append({
#                     "id": resume.id,
#                     "filename": file_obj.name,
#                     "signed_url": signed_url
#                 })

#             except Exception as e:
#                 logger.error(f"Database save failed for {file_obj.name}: {e}")
#                 return Response({"error": "Failed to save resume"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#         return Response({"uploaded_files": uploaded_files}, status=status.HTTP_201_CREATED)

# class GetSingleResumeView(APIView):
#     """Retrieve uploaded resumes with signed URLs for authorized users."""

#     def get(self, request, *args, **kwargs):
#         resumes = Resume.objects.all()

#         resume_data = []
#         for resume in resumes:
#             resume_data.append({
#                 "id": resume.id,
#                 "signed_url": resume.file_url  #retrieved signed URL
#             })
#         print(resume_data)
#         return Response({"resumes": resume_data}, status=status.HTTP_200_OK)


# class GetAllResumesView(APIView):
#     def get(self, request):
#         resumes = Resume.objects.all()
#         serializer = ResumeSerializer(resumes, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# import json
# from rest_framework.decorators import api_view
# from rest_framework.response import Response
# from mainapp.models import Resume


# @api_view(["GET"])
# def get_resumes(request):
#     resumes = Resume.objects.all()
#     formatted_resumes = []

#     for resume in resumes:
#         # ✅ Parse extracted_data if it's stored as a string
#         extracted = resume.extracted_data
       

#         # Check if extracted_data is a string and parse it
#         if isinstance(extracted, str):
#             try:
#                 extracted = json.loads(extracted)
#             except json.JSONDecodeError:
#                 extracted = {}

#         formatted_resumes.append({
#             "id": resume.id,
            
#             "file_url": resume.file_url if resume.file_url else "",
#             "name": extracted.get("name", "N/A"),
#             "role": extracted.get("experience")[-1].get("role", "-") 
#             if isinstance(extracted.get("experience"), list) and extracted.get("experience") 
#             else "-"
# ,
#             "email": extracted.get("email", "N/A"),
#             "contact": extracted.get("contact", "N/A"),
#             "location": extracted.get("location", "N/A"),
#             "applied_for": extracted.get("applied_for", "N/A"),
#             "experience": extracted.get("experience", "N/A"),
#             "skills": extracted.get("skills", []),
#             "education": extracted.get("education", "N/A"),
#             "profile_summary": extracted.get("profile_summary", "N/A"),
#         })

#     return Response(formatted_resumes)

# This is written code for get data from cookies and save in database

import json
import logging
import uuid
import os
from datetime import timedelta
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from rest_framework.decorators import api_view
from django.conf import settings
from google.cloud import storage
from mainapp.models import Resume
from mainapp.serializers import ResumeSerializer
from mainapp.utils import extract_resume_data
from mainapp.decorators import with_token_info

logger = logging.getLogger(__name__)


class UploadResumeView(APIView):
    parser_classes = [MultiPartParser]

    def generate_unique_filename(self, original_filename):
        name, ext = os.path.splitext(original_filename)
        safe_name = f"{name.replace(' ', '_')}_{uuid.uuid4().hex}{ext}"
        return safe_name

    def upload_to_gcs(self, file_obj, unique_filename):
        try:
            client = storage.Client()
            bucket = client.bucket(settings.GS_BUCKET_NAME)
            blob = bucket.blob(f"{settings.GS_LOCATION}/{unique_filename}")
            blob.upload_from_file(file_obj)

            signed_url = blob.generate_signed_url(
                expiration=timedelta(minutes=60),
                method="GET"
            )
            return signed_url
        except Exception as e:
            logger.error(f"GCS Upload Failed: {e}")
            return None

    @with_token_info
    def post(self, request, *args, **kwargs):
        logger.info(f"Received request with files: {request.FILES}")

        files = request.FILES.getlist("file")
        if not files:
            return Response({"error": "No files uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_files = []
        for file_obj in files:
            unique_filename = self.generate_unique_filename(file_obj.name)
            signed_url = self.upload_to_gcs(file_obj, unique_filename)

            if not signed_url:
                return Response({"error": f"Failed to upload {file_obj.name}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            try:
                resume = Resume.objects.create(
                    file_url=signed_url,
                    uploaded_by_id=request.role_id,
                    user_type=request.role
                )

                uploaded_files.append({
                    "id": resume.id,
                    "filename": file_obj.name,
                    "signed_url": signed_url
                })

            except Exception as e:
                logger.error(f"Database save failed for {file_obj.name}: {e}")
                return Response({"error": "Failed to save resume"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"uploaded_files": uploaded_files}, status=status.HTTP_201_CREATED)


class GetSingleResumeView(APIView):
    """Retrieve uploaded resumes with signed URLs for authorized users."""

    @with_token_info
    def get(self, request, *args, **kwargs):
        resumes = Resume.objects.filter(uploaded_by_id=request.role_id, user_type=request.role)

        resume_data = []
        for resume in resumes:
            resume_data.append({
                "id": resume.id,
                "signed_url": resume.file_url
            })
        print(resume_data)
        return Response({"resumes": resume_data}, status=status.HTTP_200_OK)


class GetAllResumesView(APIView):
    @with_token_info
    def get(self, request):
        if request.role == "admin":
            resumes = Resume.objects.all()
        else:
            resumes = Resume.objects.filter(uploaded_by_id=request.role_id, user_type=request.role)
        
        serializer = ResumeSerializer(resumes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@with_token_info
def get_resumes(request):
    """
    Get all resumes uploaded by the current HR user.
    Admin can see all resumes.
    """
    if request.role == "admin":
        resumes = Resume.objects.all()
    else:
        resumes = Resume.objects.filter(uploaded_by_id=request.role_id, user_type=request.role)

    formatted_resumes = []

    for resume in resumes:
        extracted = resume.extracted_data

        if isinstance(extracted, str):
            try:
                extracted = json.loads(extracted)
            except json.JSONDecodeError:
                extracted = {}

        formatted_resumes.append({
            "id": resume.id,
            "file_url": resume.file_url if resume.file_url else "",
            "name": extracted.get("name", "N/A"),
            "role": extracted.get("experience")[-1].get("role", "-") 
                    if isinstance(extracted.get("experience"), list) and extracted.get("experience") 
                    else "-",
            "email": extracted.get("email", "N/A"),
            "contact": extracted.get("contact", "N/A"),
            "location": extracted.get("location", "N/A"),
            "applied_for": extracted.get("applied_for", "N/A"),
            "experience": extracted.get("experience", "N/A"),
            "skills": extracted.get("skills", []),
            "education": extracted.get("education", "N/A"),
            "profile_summary": extracted.get("profile_summary", "N/A"),
        })

    return Response(formatted_resumes)


import jwt
import datetime
from django.conf import settings
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.utils.decorators import method_decorator
import json

SECRET_KEY = settings.SECRET_KEY

# Login API
@csrf_exempt
def login_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            password = data.get("password")

            if username == "admin" and password == "admin":
                token = jwt.encode(
                    {"username": username, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
                    SECRET_KEY,
                    algorithm="HS256",
                )

                response = JsonResponse({"message": "Login successful!"})
                response.set_cookie(
                    key="token",
                    value=token,
                    httponly=True,
                    samesite="Lax",
                )
                return response
            return JsonResponse({"error": "Invalid credentials"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Resume
from .utils import extract_resume_data ,save_extracted_data  
import logging

logger = logging.getLogger(__name__)

class ExtractResumeDataView(APIView):
    """Fetch one unprocessed resume, extract structured data using Gemini API, and store it in the database."""
    
    def get(self, request, *args, **kwargs):
        try:
            
            resume = Resume.objects.filter(extracted_data__isnull=True).first()
            if not resume:
                return Response({"message": "No unprocessed resumes found"}, status=status.HTTP_404_NOT_FOUND)

            extracted_data = extract_resume_data(resume.file_url)  
            if extracted_data:
                resume.extracted_data = extracted_data 
                resume.save()
                save_extracted_data(extracted_data)  

            return Response({
                "id": resume.id,
                "file_url": resume.file_url,
                "extracted_data": extracted_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error processing resume: {e}")
            return Response({"error": "Something went wrong"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Resume
from .utils import extract_filter_criteria_using_custom_parser, calculate_total_experience

def search_resumes_from_input(filters, search_query=None):
    queryset = Resume.objects.all()
    scored_resumes = []

    for resume in queryset:
        extracted_data = resume.extracted_data or {}
        match_count = 0

        # Role Match
        role_filter = filters.get("jobAppliedFor")
        if role_filter:
            roles = [exp.get("role", "") for exp in extracted_data.get("experience", [])]
            if any(role_filter.lower() in role.lower() for role in roles if role):
                match_count += 1

        #  Skills Match
        skills_filter = filters.get("skill")
        if skills_filter:
            resume_skills = extracted_data.get("skills", [])
            flat_skills = []
            if isinstance(resume_skills, dict):
                for cat_skills in resume_skills.values():
                    flat_skills.extend(cat_skills)
            else:
                flat_skills = resume_skills

            flat_skills = [s.lower().strip() for s in flat_skills]
            if skills_filter.lower().strip() in flat_skills:
                match_count += 1

        # Location Match
        location_filter = filters.get("location")
        if location_filter:
            location = (extracted_data.get("location") or "").lower()
            if location_filter.lower() in location:
                match_count += 1

        # Job Type Match
        job_type = filters.get("jobType")
        if job_type:
            resume_job_type = (extracted_data.get("job_type") or "").lower()
            if job_type.lower() in resume_job_type:
                match_count += 1

        # Experience Range Match
        experience_range = filters.get("experience")
        if experience_range:
            min_exp = int(experience_range.split('-')[0].strip())
            max_exp = int(experience_range.split('-')[1].split()[0].strip())
            total_years = calculate_total_experience(extracted_data.get("experience", []))
            if min_exp <= total_years <= max_exp:
                match_count += 1

        # Optional: Match searchQuery using simple keyword matching
        if search_query:
            query_lower = search_query.lower()
            content = json.dumps(extracted_data).lower()
            if query_lower in content:
                match_count += 1

        if match_count > 0:
            scored_resumes.append((match_count, resume))

    grouped = {5: [], 4: [], 3: [], 2: [], 1: []}
    for count, resume in scored_resumes:
        grouped[count].append(resume)

    for i in range(5, 0, -1):
        if grouped[i]:
            return sorted(grouped[i], key=lambda r: r.uploaded_at, reverse=True)

    return []


@csrf_exempt
def smart_resume_search_view(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            filters = {
                "jobAppliedFor": data.get("jobAppliedFor"),
                "location": data.get("location"),
                "skill": data.get("skill"),
                "experience": data.get("experience"),
                "jobType": data.get("jobType"),
                "role": data.get("role"),
            }
            search_query = data.get("searchQuery", "")

            print(" Filters:", filters)
            print(" Search Query:", search_query)

            results = search_resumes_from_input(filters, search_query)

            serialized_data = []
            for resume in results:
                extracted = resume.extracted_data or {}

                resume_data = {
                    "id": resume.id,
                    "file_url": resume.file_url,
                    "name": extracted.get("name", "N/A"),
                    "role": extracted.get("role", "N/A"),
                    "email": extracted.get("email", "N/A"),
                    "contact": {
                        "mobile": extracted.get("contact", {}).get("mobile", "N/A")
                    },
                    "location": extracted.get("location", "N/A"),
                    "applied_for": extracted.get("applied_for", "N/A"),
                    "experience": extracted.get("experience", []),
                    "skills": extracted.get("skills", {}),
                    "education": extracted.get("education", []),
                    "profile_summary": extracted.get("profile_summary", "N/A"),
                    "uploaded_at": resume.uploaded_at
                }

                serialized_data.append(resume_data)

            print(" Search results:", serialized_data)
            return JsonResponse(serialized_data, safe=False)

        except Exception as e:
            print(" Error:", str(e))
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

