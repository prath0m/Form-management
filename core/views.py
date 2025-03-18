from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, FormUploadForm
from django.contrib.auth.decorators import login_required
from .models import FormUpload,CustomUser,PreviousFinding,FormSubmission
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
# from google.cloud import bigquery
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
from django.contrib import messages
import json
from django.core.mail import send_mail
from django.conf import settings
from .utils import send_email_notification
from django.utils import timezone
import os
import glob
def get_visit_data(visit_type):
    # client = bigquery.Client()
    # datasets = client.list_datasets()
    # dataset_names = [dataset.dataset_id for dataset in datasets ]
    
    combined_data = []
    with open('./json/QSMV_Okinawa.json', 'r') as file:
        okinawa_data = json.load(file)
    with open('./json/QSMV_Charleston.json', 'r') as file:\
        charleston_data = json.load(file)
    
    combined_data = charleston_data + okinawa_data
    
    if visit_type == 'new_visit':
        query_table = 'combined_data'
    elif visit_type == 'okinawa':
        with open('./json/QSMV_Okinawa.json', 'r') as file:
            query_table = json.load(file)
    elif visit_type == 'charleston':
        with open('./json/QSMV_Charleston.json', 'r') as file:
            query_table = json.load(file)

    # query = f"SELECT * FROM `dfsp-prototype.project_dataset.{query_table}` LIMIT 1000"
    # query_job = client.query(query)
    results = query_table
    return results

@login_required
def parsed_user_forms(request):
    # if request.user.role == 'admin':
    #     data = get_visit_data('new_visit')
    #     res = []
    #     for row in data:
    #         file_path = row.file_input_path
    #         file_path = file_path.lstrip('Uploaded_image/').rstrip('.pdf')
    #         if file_path.isdigit():
    #             file_obj = FormUpload.objects.get(pk= file_path)
    #             file_name = file_obj.file.name.lstrip('uploads/')
    #             file_url = file_obj.file.url
    #             res.append({'row':row, "file_name": file_name, "file_url":file_url})
    #     return render(request, 'core/parsed_data.html', {"datasets":res})
    # return redirect('manage_uploads')
    if request.user.role == 'admin':
        data = []
        with open('./json/parsed_data.json', 'r') as file:
            data = json.load(file)
        return render(request, 'core/parsed_data.html', {'datasets': data})
    return redirect('manage_uploads')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'core/login.html', {'error': 'Invalid credentials'})
    return render(request, 'core/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def manage_user_uploads(request):
    if request.method == 'POST':
        # Handle file upload
        form = FormUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_instance = form.save(commit=False)
            file_instance.user = request.user
            file_instance.save()
            subject = "New File Uploaded"
            template_name = "emails/upload_notification.html"
            context = {
             "username": request.user.username,
             "file_name": file_instance.file.name,
             "uploaded_at": file_instance.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
             "file_url": request.build_absolute_uri(file_instance.file.url),
            }
            to_email = "khurrum.kaiser@cssdfspgcp.com"
            send_email_notification(subject, template_name, context, to_email)
            return redirect('manage_uploads')  # Redirect to the same page to display the updated list
    else:
        form = FormUploadForm()

    # Handle GET request (render the page)
    files = FormUpload.objects.filter(user=request.user)
    return render(request, 'core/manage_uploads.html', {'form': form, 'files': files})
@login_required
def user_uploads(request):
    files = FormUpload.objects.filter(user=request.user)
    return render(request, 'core/user_uploads.html', {'files': files})
@login_required
def admin_review(request):
    if request.user.role != 'admin':
        return redirect('dashboard')

    files = FormUpload.objects.all()
    return render(request, 'core/admin_review.html', {'files': files})

@login_required
def update_status(request, file_id, status):
    if request.user.role != 'admin':
        return redirect('dashboard')

    file_instance = FormUpload.objects.get(id=file_id)
    file_instance.status = status
    file_instance.save()
    return redirect('admin_review')

def approval_pending(request):
    return render(request, 'core/approval_pending.html')

@login_required
def approve_form(request, form_id):
    file_instance = get_object_or_404(FormUpload, id=form_id)
    file_instance.status = 'approved'
    file_instance.save()
     
    # from google.cloud import storage

    # # Initialize a client for Google Cloud Storage
    # storage_client = storage.Client()

    # # Get the bucket where you want to store the file
    # bucket = storage_client.get_bucket('dfsp_testcase_01')
    # print('bucket created')
    # # Create a new blob (file) in the specified bucket
    # file_extension = file_instance.file.name.split('.')[-1]
    # blob = bucket.blob('Uploaded_image/'+str(file_instance.pk)+'.'+file_extension)
    # print('b')

    # file_path = file_instance.file.path
    # # Upload the file from local storage to GCS
    # blob.upload_from_filename(file_path)


    subject = "Your File Has Been Approved"
    template_name = "emails/status_update_notification.html"
    form = file_instance
    context = {
        "username": form.user.username,
        "file_name": form.file.name,
        "uploaded_at": form.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
        "status": "APPROVED",
    }
    to_email = form.user.email
    send_email_notification(subject, template_name, context, to_email)

    return JsonResponse({
                'success': True})

@login_required
def okinawa_table(request, location=None):
    if request.user.role == 'admin':
        okinawa_data = [row for row in get_visit_data('okinawa')]
        charleston_data = [row for row in get_visit_data('charleston')]
        result = okinawa_data + charleston_data
        return render(request, 'core/okinawa.html', {'all_visit_data':result,'current_location':location})

    return redirect('manage_uploads')


@login_required
def reject_form(request, form_id):
    form = get_object_or_404(FormUpload, id=form_id)
    form.status = 'rejected'
    form.save()
    subject = "Your File Has Been Rejected"
    template_name = "emails/status_update_notification.html"
    context = {
     "username": form.user.username,
     "file_name": form.file.name,
     "uploaded_at": form.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
     "status": "REJECTED",}
    to_email = form.user.email
    send_email_notification(subject, template_name, context, to_email)
    return redirect('dashboard')

@login_required
def dashboard(request):
    if request.user.role == 'admin':
        all_users = CustomUser.objects.all()
        all_forms = FormUpload.objects.all().order_by('-uploaded_at')
        approved_count = FormUpload.objects.filter(status='approved').count()
        rejected_count = FormUpload.objects.filter(status='rejected').count()
        pending_count = FormUpload.objects.filter(status='pending').count()
        admin_count = CustomUser.objects.filter(role = 'admin').count()
        user_count = CustomUser.objects.filter(role = 'user').count()

        okinawa_data = get_visit_data('okinawa')

        charleston_data = get_visit_data('charleston')
        oki_data = [dict(row) for row in okinawa_data]
        charles_data = [dict(row)for row in charleston_data]
        return render(request, 'core/dashboard.html', {
            'all_users': all_users,
            'all_forms': all_forms,
            'okinawa_data': oki_data,
            'charleston_data': charles_data,
            'approved_count': approved_count,
            'rejected_count': rejected_count,
            'pending_count': pending_count,
            'admin_counts': admin_count,
            'user_counts': user_count,
        })
    return redirect('manage_uploads')

@login_required
def update_remark(request, form_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized access'}, status=403)
    
    if request.method == 'POST':
        try:
            form = get_object_or_404(FormUpload, id=form_id)
            data = json.loads(request.body)
            new_remark = data.get('remarks', '')
            
            form.remarks = new_remark
            form.save()
            
            return JsonResponse({
                'success': True,
                'new_remark': new_remark
            })
        except Exception as e:
            print("Exception : " ,e)
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def update_remark(request, form_id):
    if request.user.role != 'admin':
        return JsonResponse({'error': 'Unauthorized access'}, status=403)
    
    if request.method == 'POST':
        try:
            form = get_object_or_404(FormUpload, id=form_id)
            data = json.loads(request.body)
            new_remark = data.get('remarks', '')
            
            form.remarks = new_remark
            form.save()
            
            return JsonResponse({
                'success': True,
                'new_remark': new_remark
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)


@login_required
def form(request):
    user = request.user
    previous_findings = {
        f"previous_finding{pf.finding_number}": pf.finding_text
        for pf in PreviousFinding.objects.filter(user=user)
    }
    saved_file_path = request.GET.get("file_path", "")
    context = {
        "previous_findings": previous_findings,
        "saved_file_path": saved_file_path,
    }
    return render(request, 'core/form.html', context)

@login_required
def saved_form(request):
    user = request.user
    saved_files = glob.glob(f'media/saved_forms/{user.username}_saved_*.json')
    saved_forms = []
    for file_path in saved_files:
        filename = os.path.basename(file_path)
        saved_forms.append({"filename": filename, "file_path": file_path})
    return render(request, 'core/savedForm.html', {"saved_forms": saved_forms})

@login_required
def load_saved_form(request):
    file_path = request.GET.get('file_path', '')
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                form_data = json.load(f)
            return JsonResponse({"status": "success", "form_data": form_data})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    else:
        return JsonResponse({"status": "error", "message": "File not found"}, status=404)


@login_required
@csrf_exempt
def save_progress(request):
    user = request.user
    if request.method == "POST":
        form_data = {}
        for key, value in request.POST.lists():
            if key != 'csrfmiddlewaretoken':
                form_data[key] = value if len(value) > 1 else value[0]
        try:
            os.makedirs('media/saved_forms', exist_ok=True)
            current_time = timezone.now().strftime('%Y%m%d_%H%M%S')
            form_type = form_data.get("FormType", "")
            filename = f"{user.username}_saved_{current_time}_{form_type}.json"
            file_path = os.path.join('media/saved_forms', filename)
            form_data['saved_file_path'] = file_path
            with open(file_path, 'w') as json_file:
                json.dump(form_data, json_file, indent=4)
            
            subject = "File Saved"
            template_name = "emails/save_notification.html"
            context = {
             "username": request.user.username,
             "uploaded_at": current_time,
            }
            to_email = request.user.email
            send_email_notification(subject, template_name, context, to_email)
            return JsonResponse({
                "status": "success",
                "message": "Form progress saved!",
                "filename": filename,
                "file_path": file_path
            })
            
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=400)

@login_required
@csrf_exempt
def store_data(request):
    user = request.user
    current_time = timezone.now().strftime('%Y%m%d_%H%M%S')
    submitted_file_name = f"{user.username}_submitted_{current_time}.json"

    if request.method == "POST":
        if "field_name" in request.POST:
            field_name = request.POST.get("field_name")
            finding_text = request.POST.get("finding_text")
            try:
                finding_number = int(field_name.replace("previous_finding", ""))
                if not (1 <= finding_number <= 7):
                    raise ValueError("Finding number must be between 1 and 7")
                PreviousFinding.objects.update_or_create(
                    user=user,
                    finding_number=finding_number,
                    defaults={'finding_text': finding_text}
                )
                return JsonResponse({"status": "success", "message": "Previous finding saved!"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=500)

        form_data = {}
        for key, value in request.POST.lists():
            if key == "category[]":
                form_data["category"] = value
            elif key != 'csrfmiddlewaretoken':
                form_data[key] = value[0] if len(value) == 1 else value

        try:
            forms_dir = os.path.join(settings.MEDIA_ROOT, 'forms')
            os.makedirs(forms_dir, exist_ok=True)
            submitted_file_path = os.path.join(forms_dir, submitted_file_name)
            with open(submitted_file_path, 'w') as json_file:
                json.dump(form_data, json_file, indent=4)

            saved_file_path = request.POST.get("saved_file_path", "").strip()
            print("Received saved_file_path:", saved_file_path)
            if saved_file_path:
                if not os.path.isabs(saved_file_path):
                    absolute_path = os.path.join(settings.BASE_DIR, saved_file_path)
                else:
                    absolute_path = saved_file_path
                print("Attempting to delete:", absolute_path)
                if os.path.exists(absolute_path):
                    os.remove(absolute_path)
                    print("Saved progress file deleted.")
                else:
                    print("Saved progress file not found at:", absolute_path)
            else:
                print("No saved_file_path received from form.")

            form_type = form_data.get("FormType", "")

            submission = FormSubmission.objects.create(
                user=user,
                form_type=form_type,
                submitted_file=submitted_file_name,
                file_path = submitted_file_path
            )
            return redirect('form')

        except Exception as e:
            return HttpResponse(f"An error occurred while submitting: {e}", status=500)

    return render(request, 'core/form.html')


@login_required
def digital_form(request):
    submissions = FormSubmission.objects.order_by('-submitted_at')
    return render(request, 'core/digital_form.html', {'submissions': submissions})

@login_required
def get_submission(request, submission_id):
    try:
        submission = FormSubmission.objects.get(id=submission_id)
        base_dir = os.path.join(settings.MEDIA_ROOT, 'forms')
        file_path = os.path.join(base_dir, submission.submitted_file)
        if not os.path.exists(file_path):
            return JsonResponse({"status": "error", "message": "File not found"}, status=404)
        with open(file_path, 'r') as f:
            file_content = f.read()
        return JsonResponse({"status": "success", "content": file_content})
    except FormSubmission.DoesNotExist:
        raise Http404("Submission not found")
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
@csrf_exempt
def store_data(request):
    user = request.user
    current_time = timezone.now().strftime('%Y%m%d_%H%M%S')
    submitted_file_name = f"{user.username}_submitted_{current_time}.json"
    print('store_data triggered')
    if request.method == "POST":
        print('is post req')
        if "field_name" in request.POST:
            field_name = request.POST.get("field_name")
            finding_text = request.POST.get("finding_text")
            try:
                finding_number = int(field_name.replace("previous_finding", ""))
                if not (1 <= finding_number <= 7):
                    raise ValueError("Finding number must be between 1 and 7")
                PreviousFinding.objects.update_or_create(
                    user=user,
                    finding_number=finding_number,
                    defaults={'finding_text': finding_text}
                )
                return JsonResponse({"status": "success", "message": "Previous finding saved!"})
            except Exception as e:
                return JsonResponse({"status": "error", "message": str(e)}, status=500)
        print('a')
        form_data = {}
        for key, value in request.POST.lists():
            if key == "category[]":
                form_data["category"] = value
            elif key != 'csrfmiddlewaretoken':
                form_data[key] = value[0] if len(value) == 1 else value
        print('b')
        try:
            forms_dir = os.path.join(settings.MEDIA_ROOT, 'forms')
            os.makedirs(forms_dir, exist_ok=True)
            submitted_file_path = os.path.join(forms_dir, submitted_file_name)
            with open(submitted_file_path, 'w') as json_file:
                json.dump(form_data, json_file, indent=4)
            selected_categories = ''
            for i in range(1,8):
                print('z')
                category = 'category'+str(i)+'[]'
                if category in form_data:
                    print(form_data[category])
                    selected_categories = selected_categories + 'Category ' + str(i)+': ' +str(form_data[category]) +'\r\n'
            print(selected_categories)
            subject = "Form Submitted"
            template_name = "emails/submit_notification.html"
            context = {
             "username": request.user.username,
             "uploaded_at": current_time,
             "comments":selected_categories
            }
            to_email = request.user.email
            send_email_notification(subject, template_name, context, to_email)
            saved_file_path = request.POST.get("saved_file_path", "").strip()
            print("Received saved_file_path:", saved_file_path)
            if saved_file_path:
                if not os.path.isabs(saved_file_path):
                    absolute_path = os.path.join(settings.BASE_DIR, saved_file_path)
                else:
                    absolute_path = saved_file_path
                if os.path.exists(absolute_path):
                    os.remove(absolute_path)

            form_type = form_data.get("FormType", "")

            #BigQuery Config

            try:
                # Create a BigQuery client. If your GOOGLE_APPLICATION_CREDENTIALS is set,
                # it will use that credential.
                # client = bigquery.Client()
                # Set your BigQuery table ID in the format: project.dataset.table
                # table_id = "form-upload-452914.form_upload_dataset.form_submission"  # Change to your table's ID

                # Prepare the row. Here we assume form_data keys match your BigQuery table schema.
                # rows_to_insert = [form_data]
                # errors = client.insert_rows_json(table_id, rows_to_insert)
                if errors:
                    print("Encountered errors while inserting rows into BigQuery: {}".format(errors))
                else:
                    print("Data inserted into BigQuery table successfully.")
            except Exception as bq_error:
                print("BigQuery insertion error:", bq_error)


            submission = FormSubmission.objects.create(
                user=user,
                form_type=form_type,
                submitted_file=submitted_file_name,
                file_path = submitted_file_path
            )
            return redirect('form')

        except Exception as e:
            return HttpResponse(f"An error occurred while submitting: {e}", status=500)

    return render(request, 'core/form.html')

def kpi(request):
    return render(request, 'core/kpi.html')


def moa(request):
    return render(request, 'core/moa.html')
