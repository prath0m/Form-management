from django.urls import path
from .views import (register, login_view, logout_view,
                     dashboard,manage_user_uploads, approval_pending,
                     approve_form, reject_form, okinawa_table, update_remark, parsed_user_forms, form, store_data, load_saved_form, save_progress, saved_form,digital_form, get_submission,kpi)

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('', dashboard, name='dashboard'),
    path('okinawa-data/', okinawa_table, name='okinawa_table'),
    path('okinawa-data/<str:location>/', okinawa_table, name='okinawa_table'),
    path('manage-uploads/', manage_user_uploads, name='manage_uploads'),
    path('approval-pending/', approval_pending, name='approval_pending'),
    path('approve-form/<int:form_id>/', approve_form, name='approve_form'),
    path('reject-form/<int:form_id>/', reject_form, name='reject_form'),
    # path('all_data/', all_data, name='all_data'),
    path('update-remark/<int:form_id>/', update_remark, name='update_remark'),
    path('parsed_user_forms/', parsed_user_forms, name='parsed_user_forms'), # for parsed user forms
    path('form/', form, name='form'),
    path('store_data/', store_data, name='store_data'),
    path('save_progress/', save_progress, name='save_progress'),
    path('load_saved_form/', load_saved_form, name='load_saved_form'),
    path('saved_form/', saved_form, name='saved_form'),
    path('digital_form/', digital_form, name='digital_form'),
    path('get_submission/<int:submission_id>/', get_submission, name='get_submission'),
    path('kpi/',kpi, name='kpi'),
]
