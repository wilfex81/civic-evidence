from datetime import timedelta

from django.db import models
from django.utils import timezone

# How many days back an observation still counts as "recent" evidence.
# Older observations are not ignored, they are shown, but they cannot
# by themselves produce an "Aligned" or "Conflicting" status.
RECENCY_WINDOW_DAYS = 30


class Project(models.Model):
    """The official record: what an institution has stated about a
    civic project or public service."""

    class OfficialStatus(models.TextChoices):
        COMPLETED = "completed", "Completed"
        ONGOING = "ongoing", "Ongoing"
        PLANNED = "planned", "Planned"
        STALLED = "stalled", "Stalled"

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    summary = models.TextField(
        help_text="One or two sentences describing the project."
    )
    location = models.CharField(max_length=150)
    responsible_organization = models.CharField(max_length=200)

    official_status = models.CharField(
        max_length=20, choices=OfficialStatus.choices
    )
    official_status_date = models.DateField(
        help_text="Date the official status was recorded or announced."
    )
    source_name = models.CharField(
        max_length=200,
        help_text="Where the official claim came from, e.g. a ministry "
        "report or county gazette notice.",
    )
    source_url = models.URLField(blank=True)

    is_demo_data = models.BooleanField(
        default=True,
        help_text="Marks records seeded for demonstration rather than "
        "sourced from a real institution.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    # --- Evidence status logic -------------------------------------
    #
    # The rule is intentionally simple and fully inspectable:
    # 1. No observations at all            -> "no_evidence"
    # 2. No observations within the        -> "stale"
    #    recency window
    # 3. Recent observations all match     -> "aligned"
    #    what the official status implies
    # 4. Recent observations are a mix of  -> "conflicting"
    #    matching and non-matching, or all
    #    non-matching

    EXPECTED_OBSERVATION_STATUS = {
        OfficialStatus.COMPLETED: {"operational"},
        OfficialStatus.ONGOING: {"operational", "in_progress"},
        OfficialStatus.PLANNED: {"no_activity"},
        OfficialStatus.STALLED: {"no_activity", "not_operational"},
    }

    def recent_observations(self):
        cutoff = timezone.now().date() - timedelta(days=RECENCY_WINDOW_DAYS)
        return [
            obs for obs in self.observations.all() if obs.date_observed >= cutoff
        ]

    def evidence_status(self):
        """Returns a dict with a machine key, a display label, and the
        recent observations that produced the verdict."""
        all_obs = list(self.observations.all())
        if not all_obs:
            return {
                "key": "no_evidence",
                "label": "No evidence yet",
                "detail": "No community observations have been submitted "
                "for this record.",
                "recent": [],
            }

        recent = self.recent_observations()
        if not recent:
            newest = all_obs[0]
            return {
                "key": "stale",
                "label": "No recent evidence",
                "detail": f"The newest observation is from "
                f"{newest.date_observed:%B %d, %Y}, outside the "
                f"{RECENCY_WINDOW_DAYS}-day recency window.",
                "recent": [],
            }

        expected = self.EXPECTED_OBSERVATION_STATUS.get(
            self.official_status, set()
        )
        matches = [obs for obs in recent if obs.status in expected]
        mismatches = [obs for obs in recent if obs.status not in expected]

        if mismatches and matches:
            return {
                "key": "conflicting",
                "label": "Conflicting evidence",
                "detail": "Recent observations disagree with each other "
                "about the current state of this project.",
                "recent": recent,
            }
        if mismatches and not matches:
            return {
                "key": "conflicting",
                "label": "Conflicting evidence",
                "detail": "Recent observations do not match the official "
                "status.",
                "recent": recent,
            }
        return {
            "key": "aligned",
            "label": "Aligned evidence",
            "detail": "Recent observations match the official status.",
            "recent": recent,
        }


class Observation(models.Model):
    """A community-submitted report of what is actually being observed
    on the ground, with a stated form of supporting evidence."""

    class Status(models.TextChoices):
        OPERATIONAL = "operational", "Operational"
        NOT_OPERATIONAL = "not_operational", "Not operational"
        IN_PROGRESS = "in_progress", "In progress"
        NO_ACTIVITY = "no_activity", "No activity observed"
        OTHER = "other", "Other"

    class EvidenceType(models.TextChoices):
        PHOTO = "photo", "Photo"
        VIDEO = "video", "Video"
        DOCUMENT = "document", "Document"
        TESTIMONY = "testimony", "Testimony / eyewitness account"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="observations"
    )
    date_observed = models.DateField()
    status = models.CharField(max_length=20, choices=Status.choices)
    description = models.TextField(
        help_text="What was observed, in the reporter's own words."
    )
    evidence_type = models.CharField(
        max_length=20, choices=EvidenceType.choices
    )
    evidence_note = models.CharField(
        max_length=255,
        blank=True,
        help_text="A short note on the evidence, e.g. a photo caption "
        "or where a document can be found.",
    )
    submitted_by = models.CharField(
        max_length=100, blank=True, default="Anonymous"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_observed", "-created_at"]

    def __str__(self):
        return f"{self.project.name} — {self.date_observed} — {self.status}"
