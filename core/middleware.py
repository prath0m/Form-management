from django.shortcuts import redirect
from django.urls import resolve

class AdminApprovalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_url_name = resolve(request.path_info).url_name
        allowed_urls = ['approval_pending','logout']
        if request.user.is_authenticated and request.user.role == 'admin' and not request.user.is_authorized and current_url_name not in allowed_urls :
            return redirect('approval_pending')  # Redirect unapproved admins to a "Pending Approval" page
        return self.get_response(request)
