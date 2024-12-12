from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, FormUploadForm
from django.contrib.auth.decorators import login_required
from .models import FormUpload
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@login_required
def dashboard(request):
    if request.user.role == 'admin':
        return render(request, 'core/admin_dashboard.html')
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