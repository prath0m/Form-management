from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'status', 'is_authorized')
    list_filter = ('role', 'status')
    actions = ['approve_admins', 'deny_admins']

    def approve_admins(self, request, queryset):
        queryset.filter(role='admin', status='pending').update(status='approved', is_authorized=True)
        self.message_user(request, "Selected admins have been approved.")
    approve_admins.short_description = "Approve selected admin accounts"

    def deny_admins(self, request, queryset):
        queryset.filter(role='admin', status='pending').update(status='denied', is_authorized=False)
        self.message_user(request, "Selected admins have been denied.")
    deny_admins.short_description = "Deny selected admin accounts"