import json

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import transaction
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ActivityForm, ProjectForm, RegisterForm, WorkForm
from .models import Activity, ActivityPhoto, Project, UserProfile, Work


def spa(request):
    return render(request, "data_entry/spa.html")


def home(request):
    return render(request, "data_entry/home.html")


def about(request):
    return render(request, "data_entry/about.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("data_entry:projects")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, "Berhasil masuk. Selamat datang!")
            return redirect("data_entry:projects")
    else:
        form = AuthenticationForm(request)
    return render(request, "data_entry/login.html", {"form": form})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("data_entry:projects")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user, nim=form.cleaned_data["nim"])
            login(request, user)
            messages.success(request, "Akun berhasil dibuat.")
            return redirect("data_entry:projects")
    else:
        form = RegisterForm()
    return render(request, "data_entry/register.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "Anda sudah keluar dari akun.")
    return redirect("data_entry:home")


@login_required
def projects(request):
    q = request.GET.get("q", "").strip()
    project_form = ProjectForm()

    if request.method == "POST":
        wizard_payload = request.POST.get("wizard_payload", "").strip()
        if wizard_payload:
            try:
                payload = json.loads(wizard_payload)
            except json.JSONDecodeError:
                messages.error(request, "Format data wizard tidak valid.")
                return redirect("data_entry:projects")

            try:
                with transaction.atomic():
                    project = Project.objects.create(
                        owner=request.user,
                        name=payload["project"]["name"],
                        description=payload["project"]["description"],
                        location=payload["project"]["location"],
                        start_date=payload["project"]["startDate"],
                        end_date=payload["project"]["endDate"],
                        executor=payload["project"]["executor"],
                        supervisor=payload["project"]["supervisor"],
                    )

                    for work_data in payload.get("works", []):
                        work = Work.objects.create(
                            project=project,
                            name=work_data["name"],
                            description=work_data["description"],
                            location=work_data["location"],
                            start_date=work_data["startDate"],
                            end_date=work_data["endDate"],
                            executor=work_data["executor"],
                            supervisor=work_data["supervisor"],
                            category=work_data["category"],
                        )
                        for act in work_data.get("activities", []):
                            Activity.objects.create(
                                work=work,
                                name=act["name"],
                                execution_time=act["executionTime"],
                                executor=act["executor"],
                                done=False,
                            )
            except Exception:
                messages.error(request, "Gagal membuat proyek dari wizard.")
                return redirect("data_entry:projects")

            messages.success(request, "Proyek berhasil dibuat (wizard).")
            return redirect("data_entry:projects")

        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            project = project_form.save(commit=False)
            project.owner = request.user
            project.save()
            messages.success(request, "Proyek berhasil dibuat.")
            return redirect("data_entry:projects")

    queryset = Project.objects.filter(owner=request.user)
    if q:
        queryset = queryset.filter(name__icontains=q) | queryset.filter(
            description__icontains=q
        )
    return render(
        request,
        "data_entry/projects.html",
        {
            "projects": queryset.distinct(),
            "project_form": project_form,
            "q": q,
        },
    )


@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    active_category = request.GET.get("category", "engineering")
    q = request.GET.get("q", "").strip()

    work_form = WorkForm(initial={"category": active_category})

    if request.method == "POST":
        if project.is_closed:
            messages.error(request, "Proyek sudah ditutup.")
            return redirect("data_entry:project_detail", project_id=project.id)

        work_form = WorkForm(request.POST)
        if work_form.is_valid():
            work = work_form.save(commit=False)
            work.project = project
            work.save()
            messages.success(request, "Pekerjaan berhasil ditambahkan.")
            return redirect(
                f"{project.get_absolute_url()}?category={work.category}"
            )

    works = project.works.filter(category=active_category)
    if q:
        works = works.filter(name__icontains=q) | works.filter(description__icontains=q)

    return render(
        request,
        "data_entry/project_detail.html",
        {
            "project": project,
            "works": works.distinct(),
            "work_form": work_form,
            "active_category": active_category,
            "q": q,
        },
    )


@login_required
def work_detail(request, project_id, work_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    work = get_object_or_404(Work, id=work_id, project=project)
    q = request.GET.get("q", "").strip()
    activity_form = ActivityForm()

    if request.method == "POST" and not project.is_closed:
        activity_form = ActivityForm(request.POST)
        if activity_form.is_valid():
            activity = activity_form.save(commit=False)
            activity.work = work
            activity.save()
            messages.success(request, "Aktivitas berhasil ditambahkan.")
            return redirect(
                "data_entry:work_detail", project_id=project.id, work_id=work.id
            )

    activities = work.activities.all()
    if q:
        activities = activities.filter(name__icontains=q) | activities.filter(
            executor__icontains=q
        )

    return render(
        request,
        "data_entry/work_detail.html",
        {
            "project": project,
            "work": work,
            "activities": activities.distinct(),
            "activity_form": activity_form,
            "q": q,
        },
    )


@login_required
@require_POST
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    project.delete()
    messages.info(request, "Proyek berhasil dihapus.")
    return redirect("data_entry:projects")


@login_required
@require_POST
def close_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    project.is_closed = True
    project.status = "Selesai"
    project.save(update_fields=["is_closed", "status"])
    messages.success(request, "Proyek ditutup.")
    return redirect("data_entry:project_detail", project_id=project.id)


@login_required
@require_POST
def delete_work(request, project_id, work_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    work = get_object_or_404(Work, id=work_id, project=project)
    if project.is_closed:
        return HttpResponseForbidden("Proyek sudah ditutup.")
    work.delete()
    messages.info(request, "Pekerjaan dihapus.")
    return redirect("data_entry:project_detail", project_id=project.id)


@login_required
@require_POST
def delete_activity(request, project_id, work_id, activity_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    work = get_object_or_404(Work, id=work_id, project=project)
    activity = get_object_or_404(Activity, id=activity_id, work=work)
    if project.is_closed:
        return HttpResponseForbidden("Proyek sudah ditutup.")
    activity.delete()
    messages.info(request, "Aktivitas dihapus.")
    return redirect("data_entry:work_detail", project_id=project.id, work_id=work.id)


@login_required
@require_POST
def toggle_activity(request, project_id, work_id, activity_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    work = get_object_or_404(Work, id=work_id, project=project)
    activity = get_object_or_404(Activity, id=activity_id, work=work)
    if project.is_closed:
        return HttpResponseForbidden("Proyek sudah ditutup.")
    activity.done = not activity.done
    activity.save(update_fields=["done"])
    messages.success(request, "Status aktivitas diperbarui.")
    return redirect("data_entry:work_detail", project_id=project.id, work_id=work.id)


@login_required
@require_POST
def update_evaluation(request, project_id, work_id, activity_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    work = get_object_or_404(Work, id=work_id, project=project)
    activity = get_object_or_404(Activity, id=activity_id, work=work)
    if project.is_closed:
        return HttpResponseForbidden("Proyek sudah ditutup.")

    activity.evaluation = request.POST.get("evaluation", "").strip()
    activity.additional_plan = request.POST.get("additional_plan", "").strip()
    activity.save(update_fields=["evaluation", "additional_plan"])
    messages.success(request, "Evaluasi disimpan.")
    return redirect("data_entry:work_detail", project_id=project.id, work_id=work.id)


@login_required
@require_POST
def upload_activity_photos(request, project_id, work_id, activity_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    work = get_object_or_404(Work, id=work_id, project=project)
    activity = get_object_or_404(Activity, id=activity_id, work=work)
    if project.is_closed:
        return HttpResponseForbidden("Proyek sudah ditutup.")

    for uploaded in request.FILES.getlist("images"):
        ActivityPhoto.objects.create(activity=activity, image=uploaded)

    messages.success(request, "Dokumentasi berhasil ditambahkan.")
    return redirect("data_entry:work_detail", project_id=project.id, work_id=work.id)
