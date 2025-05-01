from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from mainapp import views 
from mainapp.views import GetAllResumesView,UploadResumeView,GetSingleResumeView,ExtractResumeDataView,get_resumes,login_view,smart_resume_search_view
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Django login and logout urls
    path("admin/", admin.site.urls),
    # This is the main API for uploading resumes,extracting data and getting the resumes
    path("api/upload-resumes/", UploadResumeView.as_view(), name="upload-resumes"),
    path("api/get-resume/<int:resume_id>/", GetSingleResumeView.as_view(), name="get-resume"),
    path("api/get_resumes/",views.get_resumes, name="get-resumes"),
    path("api/get-resumes/", GetAllResumesView.as_view(), name="get-resumes"),
    path("api/extract-resume-data/", ExtractResumeDataView.as_view(), name="extract-resume-data"),
    path("api/smart-search/",views.smart_resume_search_view, name="smart-resume-search"),
    
    # path("protected_view/", protected_view, name="protected_view")
    path("api/login/", login_view, name="login"),
    # path("api/csrf/",views.get_csrf_token),
    # path("api/verify-token/",views.verify_token ,name="verify-token"),
   
    # This api is used to send for emails and to get the email types and tags , create email template
    path("api/quill-upload/",views.quill_upload, name="quill_upload"),
    path("api/send-email/", views.send_email_api, name="send_email_api"),
    path("api/email_types/", views.email_types_api, name="email_types_api"),
    path("api/email-tags/",views.get_email_tags, name="get-email-tags"),
    path('api/create-email-template/', views.create_email_template, name='create-email-template'),
   
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



















































































































# from django.contrib import admin
# from django.urls import path, include
# from django.conf import settings
# from django.conf.urls.static import static
# from mainapp import views  # Import views from mainapp
# from mainapp.views import BulkResumeUploadView  # Import specific views if needed

# urlpatterns = [
#     # Django Admin
#     path("admin/", admin.site.urls),

#     # Resume Upload APIs
#     path("api/upload-resumes/", BulkResumeUploadView.as_view(), name="upload-resumes"),
#     # path("api/upload-resumes-function/", views.upload_resumes, name="upload_resumes"),
    
#     # Quill File Upload API
#     path("api/quill-upload/", views.quill_upload, name="quill_upload"),

#     # Email APIs
#     path("api/send-email/", views.send_email_api, name="send_email_api"),
#     path("api/email-types/", views.email_types_api, name="email_types_api"),
#     path("api/email-tags/", views.get_email_tags, name="get-email-tags"),
#     path("api/create-email-template/", views.create_email_template, name="create-email-template"),
# ]

# # Serve media files during development
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)






















