from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Observation, Project


class EvidenceStatusTests(TestCase):
	def setUp(self):
		self.project = Project.objects.create(
			name="Test Water Project",
			slug="test-water-project",
			summary="A test civic project.",
			location="Test County",
			responsible_organization="Test County Government",
			official_status=Project.OfficialStatus.ONGOING,
			official_status_date=timezone.localdate(),
			source_name="Test source",
		)

	def test_conflicting_verdict_shows_independent_reporters_and_next_step(self):
		Observation.objects.create(
			project=self.project,
			date_observed=timezone.localdate(),
			status=Observation.Status.OPERATIONAL,
			description="Water is flowing.",
			evidence_type=Observation.EvidenceType.PHOTO,
			submitted_by="Reporter A",
		)
		Observation.objects.create(
			project=self.project,
			date_observed=timezone.localdate(),
			status=Observation.Status.NOT_OPERATIONAL,
			description="The tap is dry.",
			evidence_type=Observation.EvidenceType.TESTIMONY,
			submitted_by="Reporter B",
		)

		evidence = self.project.evidence_status()

		self.assertEqual(evidence["key"], "conflicting")
		self.assertEqual(evidence["reporter_count"], 2)
		self.assertIn("Submit your own observation", evidence["next_step"])

		response = self.client.get(
			reverse("project_detail", kwargs={"slug": self.project.slug})
		)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Based on 2 independent reporters.")
		self.assertContains(response, "Next step:")
