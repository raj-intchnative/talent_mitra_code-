from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import *


@admin.register(CreateEmailTemplate)
class CreateEmailTemplateAdmin(admin.ModelAdmin):
    list_display = (
        "Email_Template_Id",
        "Email_Template_Description",
        "BoActive",
        "Sender_Email_Id",
        
    )

    def preview_body_html(self, obj):
        """Display a small preview of the HTML body in the admin panel."""
        return mark_safe(obj.Body_Html[:100] + "...") if obj.Body_Html else ""

    preview_body_html.short_description = "Body Preview"

    search_fields = ("Email_Template_Id", "Email_Template_Description", "Subject")
    list_filter = ("BoActive", "Sender_Email_Id")
    ordering = ("Email_Template_Id",)


@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = (
        "email_template",
        "user_type",
        "email_to",
        "email_cc",
        "email_bcc",
        "reply_to_email",
        "email_send_date",
        "email_subject",
        "email_deliver_status",
        "retry_count",
        "ses_message_id",
    )

    search_fields = ("email_to", "email_subject", "ses_message_id")
    list_filter = ("email_deliver_status", "email_send_date", "email_template")
    ordering = ("-email_send_date",)
    date_hierarchy = "email_send_date"

    actions = ["mark_as_failed", "mark_as_delivered", "reset_retry_count"]

    def mark_as_failed(self, request, queryset):
        """Mark selected emails as failed."""
        queryset.update(email_deliver_status="Failed")

    mark_as_failed.short_description = "Mark selected emails as Failed"

    def mark_as_delivered(self, request, queryset):
        """Mark selected emails as delivered."""
        queryset.update(email_deliver_status="Delivered")

    mark_as_delivered.short_description = "Mark selected emails as Delivered"

    def reset_retry_count(self, request, queryset):
        """Reset retry count for failed emails."""
        queryset.update(retry_count=0)

    reset_retry_count.short_description = "Reset retry count"


@admin.register(EmailTag)
class EmailTagAdmin(admin.ModelAdmin):
    list_display = ['name']
    
    
    

# API KEY SECRET KEY
from django.contrib import admin
from mainapp.models import APIKey


class APIKeyAdmin(admin.ModelAdmin):
    list_display = ("user", "key", "is_active", "created_at")
    readonly_fields = ("key",)
    search_fields = ("user__username", "key")


admin.site.register(APIKey, APIKeyAdmin)
