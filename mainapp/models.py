from django.db import models
from django_quill.fields import QuillField


class CreateEmailTemplate(models.Model):
    EMAIL_CHOICES = [("info@talentmitra.com", "info@talentmitra.com"),("info@cvmitra.com", "info@cvmitra.com"),("info@jobmitra.com", "info@jobmitra.com"),]
    USER_ROLES = [
        ("System Admin", "System Admin"),
        ("Recruiter Id", "Recruiter Id"),
    ]
     
    Email_Template_Id = models.CharField(max_length=100,unique=True)
    Email_Template_Description = models.CharField(max_length=500)
    BoActive = models.BooleanField(default=True)
    Header_Image_Location = models.ImageField(upload_to="headers/", blank=True, null=True)
    Footer_Image_Location = models.ImageField(upload_to="footers/", blank=True, null=True)
    Email_Template_Subject = models.CharField(max_length=300)
    Body_Html=models.TextField()
    Sender_Email_Id = models.CharField(max_length=255, choices=EMAIL_CHOICES, default="info@jobmitra.com")
    Reply_To_Email_Id = models.EmailField(max_length=255, blank=True, null=True)
    Created_User_Id = models.CharField(max_length=50, choices=USER_ROLES, default="System Admin")
    
    def __str__(self):
        return f"{self.Email_Template_Id} - {self.Email_Template_Subject}"


class EmailLog(models.Model):
    email_template = models.ForeignKey(CreateEmailTemplate,on_delete=models.SET_NULL,null=True,blank=True,related_name="email_logs",)  # ForeignKey to CreateEmailTemplate instead of EmailType
    user_type = models.CharField(max_length=100)
    email_to = models.EmailField()
    email_cc = models.TextField(blank=True, null=True)
    email_bcc = models.TextField(blank=True, null=True)
    reply_to_email = models.EmailField(blank=True, null=True)  # Field for Reply-To Email
    email_send_date = models.DateTimeField(auto_now_add=True)
    email_subject = models.CharField(max_length=300)
    email_body = models.TextField()
    email_deliver_status = models.CharField(max_length=50,choices=[("Delivered", "Delivered"),("Failed", "Failed"),("Pending", "Pending"),],default="Pending",)
    email_failure_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    ses_message_id = models.CharField(max_length=255, blank=True, null=True)

    def increment_retry(self):
        """Increase retry count when email fails."""
        self.retry_count += 1
        self.save()

    def __str__(self):
        return f"{self.email_template.Email_Template_Id if self.email_template else 'No Template'} | Subject: {self.email_subject} | Status: {self.email_deliver_status}"


from django.db import models

class EmailTag(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    
# #API SECRECT KEY

from django.db import models
from django.contrib.auth.models import User
import secrets


class APIKey(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    key = models.CharField(max_length=200, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(100)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.key}"


from django.db import models


class Resume(models.Model):
    uploaded_by_id=models.IntegerField(blank=True, null=True)
    user_type=models.CharField(max_length=255,null=True, blank=True)
    file_url = models.TextField()
    extracted_data = models.JSONField(blank=True, null=True)  
    uploaded_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.file_url


class Candidate(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True) 
    location = models.CharField(max_length=255, blank=True, null=True)
    profile_summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Education Model (Candidate's Education History)
class CandidateEducation(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="education")
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    start_date = models.CharField(max_length=50, blank=True, null=True)
    end_date = models.CharField(max_length=50, blank=True, null=True)
    gpa = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.candidate.name} - {self.degree}"

# Experience Model (Candidate's Work Experience)
class CandidateExperience(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="experience")
    company = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    start_date = models.CharField(max_length=50, blank=True, null=True)
    end_date = models.CharField(max_length=50, blank=True, null=True)
    responsibilities = models.TextField()

    def __str__(self):
        return f"{self.candidate.name} - {self.company}"

# Skills Model (Candidate's Skills)
class CandidateSkill(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="skills")
    skill_type = models.CharField(max_length=50)  # Example: Languages, Frameworks
    skill_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.candidate.name} - {self.skill_type}: {self.skill_name}"

# Total Experience Model (Candidate's Total Experience in Years & Months)
class CandidateTotalExperience(models.Model):
    candidate = models.OneToOneField(Candidate, on_delete=models.CASCADE, related_name="total_experience")
    total_years = models.IntegerField(default=0)
    total_months = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.candidate.name} - {self.total_years} Years, {self.total_months} Months"


# Job Form Model (Job Posting Form)
# Ye model job posting ke liye hai, jismein recruiter ya employer job ki details bhar sakta hai.    

class JobForm(models.Model):
    form_id = models.AutoField(primary_key=True)
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    company_description = models.TextField()
    job_description = models.TextField()

    # Enums ko CharField ke roop mein treat karte hain
    work_type = models.CharField(
        max_length=20,
        choices=[('Remote', 'Remote'), ('Hybrid', 'Hybrid'), ('On-Site', 'On-Site')]
    )
    job_type = models.CharField(
        max_length=20,
        choices=[('Full-time', 'Full-time'), ('Part-time', 'Part-time'),
                 ('Contract', 'Contract'), ('Internship', 'Internship')]
    )
    skills = models.TextField()
    experience_level = models.CharField(
        max_length=20,
        choices=[('Fresher', 'Fresher'), ('Intermediate', 'Intermediate'),
                 ('Senior', 'Senior'), ('Expert', 'Expert')]
    )
    application_collection = models.CharField(
        max_length=20,
        choices=[('Email', 'Email'), ('Link', 'Link')]
    )
    application_source = models.CharField(max_length=250)
    is_reject = models.BooleanField()
    reject_message = models.CharField(max_length=2100)
    created_at = models.DateTimeField()
    is_active = models.BooleanField()
    maxed_retry = models.IntegerField()
    recruiter_id = models.IntegerField()
    is_expired = models.BooleanField()
    number_of_applicants = models.IntegerField()

    class Meta:
        db_table = 'jobforms'
        managed = False  # Django will not try to create or migrate this table
