from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.http import require_POST

from .forms import ProfileForm, RegisterForm, TaskForm
from .models import Task


def dashboard(request):
    if not request.user.is_authenticated:
        return render(request, "tasks/home.html")
    tasks = Task.objects.filter(user=request.user)
    today = timezone.localdate()
    pending = tasks.filter(status="Pending")
    context = {
        "total_count": tasks.count(),
        "pending_count": pending.count(),
        "completed_count": tasks.filter(status="Completed").count(),
        "upcoming_tasks": pending.filter(due_date__gte=today).order_by("due_date")[:5],
        "overdue_count": pending.filter(due_date__lt=today).count(),
        "deadline_tasks": pending.filter(due_date__lte=today + timedelta(days=2)).order_by("due_date"),
        "today": today,
        "tomorrow": today + timedelta(days=1),
    }
    return render(request, "tasks/dashboard.html", context)


def register(request):
    if request.user.is_authenticated:
        return redirect("tasks:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your account is ready. Welcome!")
        return redirect("tasks:dashboard")
    return render(request, "tasks/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("tasks:dashboard")
    form = AuthenticationForm(request, data=request.POST or None)
    for field in form.fields.values():
        field.widget.attrs["class"] = "form-control"
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        return redirect(request.GET.get("next") or "tasks:dashboard")
    return render(request, "tasks/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have been signed out.")
    return redirect("tasks:login")


@login_required
def task_list(request):
    tasks = Task.objects.filter(user=request.user)
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    priority = request.GET.get("priority", "")
    if query:
        tasks = tasks.filter(Q(title__icontains=query) | Q(subject__icontains=query) | Q(description__icontains=query))
    if status in {"Pending", "Completed"}:
        tasks = tasks.filter(status=status)
    if priority in {"Low", "Medium", "High"}:
        tasks = tasks.filter(priority=priority)
    tasks = tasks.order_by("status", "due_date", "-created_at")
    return render(request, "tasks/task_list.html", {
        "tasks": tasks, "query": query, "selected_status": status,
        "selected_priority": priority, "today": timezone.localdate(),
        "tomorrow": timezone.localdate() + timedelta(days=1),
        "soon_cutoff": timezone.localdate() + timedelta(days=2),
    })


@login_required
def task_create(request):
    form = TaskForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        task = form.save(commit=False)
        task.user = request.user
        task.save()
        messages.success(request, "Task added.")
        return redirect("tasks:task_list")
    return render(request, "tasks/task_form.html", {"form": form, "page_title": "Add a task", "button_label": "Save task"})


@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    form = TaskForm(request.POST or None, instance=task)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Task updated.")
        return redirect("tasks:task_list")
    return render(request, "tasks/task_form.html", {"form": form, "page_title": "Edit task", "button_label": "Save changes", "task": task})


@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == "POST":
        task.delete()
        messages.success(request, "Task deleted.")
        return redirect("tasks:task_list")
    return render(request, "tasks/task_confirm_delete.html", {"task": task})


@login_required
@require_POST
def task_toggle(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    task.status = "Pending" if task.status == "Completed" else "Completed"
    task.save(update_fields=["status"])
    messages.success(request, "Task marked " + task.status.lower() + ".")
    return redirect(request.POST.get("next") or "tasks:task_list")


@login_required
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
        return redirect("tasks:profile")
    return render(request, "tasks/profile.html", {"form": form})
