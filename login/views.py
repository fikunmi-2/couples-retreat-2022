from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import *
from django.contrib.auth.models import User
from website.models import Registered

def admin_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect('view-registered')
            elif user.is_staff:
                return redirect('labourer_dashboard')
            else:
                messages.warning(request, "You do not have the right permissions.")
                return redirect('admin_login')
        else:
            messages.error(request, "Login error. Try again...")
            return redirect('admin_login')
    else:
        return render(request, 'admin_login.html', {})


def admin_logout(request):
    logout(request)
    messages.success(request, "You were logged out.")
    return redirect('home')

def create_user(request):
    if not request.user.is_superuser or not request.user.is_active:
        messages.warning(request,
                         "You do not have permission to access this page. Please login.",
                         extra_tags='safe')
        return redirect('admin_login')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user_list')  # You can update this later
    else:
        form = CustomUserCreationForm()

    return render(request, 'create_user.html', {'form': form})

def user_list(request):
    if not request.user.is_superuser:
        messages.warning(request,
                         "You do not have permission to access this page. Please login.",
                         extra_tags='safe')
        return redirect('admin_login')

    both = User.objects.filter(is_superuser=True, is_staff=True).order_by('-date_joined')
    superusers_only = User.objects.filter(is_superuser=True, is_staff=False).order_by('-date_joined')
    labourers_only = User.objects.filter(is_superuser=False, is_staff=True).order_by('-date_joined')

    return render(request, 'user_list.html', {
        'both': both,
        'superusers_only': superusers_only,
        'labourers_only': labourers_only
    })

def view_labourer_couples(request, user_id):
    if not request.user.is_superuser:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('admin_login')

    labourer = get_object_or_404(User, pk=user_id, is_staff=True)
    couples = Registered.objects.filter(labourer=labourer).order_by('s_name')

    return render(request, 'labourer_couples.html', {
        'labourer': labourer,
        'couples': couples
    })

def edit_user(request, user_id):
    if not request.user.is_superuser:
        messages.warning(request,
                         "You do not have permission to access this page. Please login.",
                         extra_tags='safe')
        return redirect('admin_login')

    user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_list')
    else:
        form = EditUserForm(instance=user)

    return render(request, 'edit_user.html', {'form': form, 'user_obj': user})

def labourer_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to access this page.")
        return redirect('admin_login')

    registered_list = Registered.objects.filter(labourer=request.user).order_by('-created_at')

    return render(request, "labourer_dashboard.html", {
        "registered_list": registered_list
    })

def assign_labourers(request):
    if not request.user.is_superuser:
        messages.warning(request, "You do not have permission to access this page.")
        return redirect('admin_login')

    labourers = User.objects.filter(is_staff=True).order_by('username')
    search_query = request.GET.get('search')
    search_results = None

    if search_query:
        search_results = Registered.objects.filter(s_name__icontains=search_query).order_by('created_at')

    unassigned = Registered.objects.filter(labourer__isnull=True).order_by('created_at')
    assigned = Registered.objects.filter(labourer__isnull=False).order_by('created_at')

    if request.method == 'POST':
        if 'auto_assign' in request.POST:
            to_assign = unassigned

            for couple in to_assign:
                least_loaded = min(labourers, key=lambda l: l.assigned_couples.count())
                couple.labourer = least_loaded
                couple.save()

            messages.success(request, f"Automatically assigned {len(to_assign)} couples.")
            return redirect('assign_labourers')

        elif 'manual_assign' in request.POST:
            labourer_id = request.POST.get('labourer_id')
            couple_ids = request.POST.getlist('couple_ids')

            if not labourer_id or not couple_ids:
                messages.error(request, "Please select at least one couple and a labourer.")
                return redirect('assign_labourers')

            labourer = User.objects.get(id=labourer_id)
            couples = Registered.objects.filter(id__in=couple_ids)

            for couple in couples:
                couple.labourer = labourer
                couple.save()

            messages.success(request, f"Assigned {len(couples)} couples to {labourer.username}.")
            return redirect('assign_labourers')

    return render(request, 'assign_labourers.html', {
        'labourers': labourers,
        'unassigned': unassigned,
        'assigned': assigned,
        'search_results': search_results,
        'search_query': search_query,
    })
