from django.urls import path
from .views import (register, login_view, logout_view,
                     dashboard,manage_user_uploads, approval_pending)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', dashboard, name='dashboard'),
    path('manage-uploads/', manage_user_uploads, name='manage_uploads'),
    path('approval-pending/', approval_pending, name='approval_pending'),


]