from django import forms
from .models import CreateEmailTemplate

class EmailForm(forms.Form):
    Email_From = forms.EmailField(label="Email From",max_length=200,widget=forms.EmailInput(attrs={"class": "form-control", "placeholder": "Enter sender email address"}),)
    Email_To = forms.EmailField(label="Email To",max_length=200,widget=forms.EmailInput(attrs={"class": "form-control","placeholder": "Enter recipient email address",}),)
    Email_Type = forms.ChoiceField(
        label="Email Type",
        choices=[
            (et.Email_Template_Id, et.Email_Template_Description)
            for et in CreateEmailTemplate.objects.filter(BoActive=True)
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
    )
