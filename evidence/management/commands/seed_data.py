import json
from datetime import timedelta

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from evidence.models import Observation, Project


class Command(BaseCommand):
    help = (
        "Load demonstration projects and observations from data/projects.json "
        "and data/observations.json. Dates in those files are given as "
        "'days_ago' and are resolved relative to when this command runs, so "
        "the seeded evidence always looks recent in a demo."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Delete existing Project and Observation rows before seeding.",
        )

    def handle(self, *args, **options):
        data_dir = settings.BASE_DIR / "data"
        today = timezone.now().date()

        if options["flush"]:
            Observation.objects.all().delete()
            Project.objects.all().delete()
            self.stdout.write("Cleared existing projects and observations.")

        with open(data_dir / "projects.json") as f:
            projects_data = json.load(f)

        created_projects = 0
        for row in projects_data:
            status_date = today - timedelta(days=row["official_status_days_ago"])
            _, created = Project.objects.update_or_create(
                slug=row["slug"],
                defaults={
                    "name": row["name"],
                    "summary": row["summary"],
                    "location": row["location"],
                    "responsible_organization": row["responsible_organization"],
                    "official_status": row["official_status"],
                    "official_status_date": status_date,
                    "source_name": row["source_name"],
                    "source_url": row.get("source_url", ""),
                    "is_demo_data": True,
                },
            )
            created_projects += int(created)

        with open(data_dir / "observations.json") as f:
            observations_data = json.load(f)

        created_observations = 0
        for row in observations_data:
            project = Project.objects.get(slug=row["project_slug"])
            date_observed = today - timedelta(days=row["date_observed_days_ago"])
            _, created = Observation.objects.update_or_create(
                project=project,
                date_observed=date_observed,
                status=row["status"],
                description=row["description"],
                defaults={
                    "evidence_type": row["evidence_type"],
                    "evidence_note": row.get("evidence_note", ""),
                    "submitted_by": row.get("submitted_by") or "Anonymous",
                },
            )
            created_observations += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {Project.objects.count()} projects "
                f"({created_projects} new) and {Observation.objects.count()} "
                f"observations ({created_observations} new)."
            )
        )
