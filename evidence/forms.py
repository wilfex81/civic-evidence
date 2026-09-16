from django import forms

from .models import Observation


class ObservationForm(forms.ModelForm):
    class Meta:
        model = Observation
        fields = [
            "date_observed",
            "status",
            "description",
            "evidence_type",
            "evidence_note",
            "submitted_by",
        ]
        widgets = {
            "date_observed": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(
                attrs={"rows": 3, "placeholder": "What did you see, and where?"}
            ),
            "evidence_note": forms.TextInput(
                attrs={"placeholder": "e.g. Photo taken at the site entrance"}
            ),
            "submitted_by": forms.TextInput(
                attrs={"placeholder": "Optional — leave blank to stay anonymous"}
            ),
        }
