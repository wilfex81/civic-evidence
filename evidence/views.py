from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from .forms import ObservationForm
from .models import Project


def home(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "").strip()

    projects = Project.objects.all()
    if query:
        projects = projects.filter(name__icontains=query) | projects.filter(
            location__icontains=query
        )
    if status_filter:
        projects = projects.filter(official_status=status_filter)

    # Evidence status is computed per project so search results show the
    # same verdict as the detail page, not just the official status.
    project_cards = []
    for project in projects.distinct():
        project_cards.append(
            {"project": project, "evidence": project.evidence_status()}
        )

    context = {
        "project_cards": project_cards,
        "query": query,
        "status_filter": status_filter,
        "status_choices": Project.OfficialStatus.choices,
        "total_projects": Project.objects.count(),
    }
    return render(request, "evidence/home.html", context)


def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    evidence = project.evidence_status()
    observations = project.observations.all()
    recent_ids = {obs.id for obs in evidence["recent"]}

    context = {
        "project": project,
        "evidence": evidence,
        "observations": observations,
        "recent_ids": recent_ids,
    }
    return render(request, "evidence/project_detail.html", context)


def submit_observation(request, slug):
    project = get_object_or_404(Project, slug=slug)

    if request.method == "POST":
        form = ObservationForm(request.POST)
        if form.is_valid():
            observation = form.save(commit=False)
            observation.project = project
            if not observation.submitted_by:
                observation.submitted_by = "Anonymous"
            observation.save()
            messages.success(request, _("Observation submitted."))
            return redirect("project_detail", slug=project.slug)
    else:
        form = ObservationForm()

    return render(
        request, "evidence/submit_observation.html", {"project": project, "form": form}
    )