from django import forms
from django.utils.translation import gettext_lazy

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
        labels = {
            "date_observed": gettext_lazy("Date observed"),
            "status": gettext_lazy("Status"),
            "description": gettext_lazy("Description"),
            "evidence_type": gettext_lazy("Evidence type"),
            "evidence_note": gettext_lazy("Evidence note"),
            "submitted_by": gettext_lazy("Your name"),
        }
        widgets = {
            "date_observed": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": gettext_lazy("What did you see, and where?"),
                }
            ),
            "evidence_note": forms.TextInput(
                attrs={
                    "placeholder": gettext_lazy("e.g. Photo taken at the site entrance")
                }
            ),
            "submitted_by": forms.TextInput(
                attrs={
                    "placeholder": gettext_lazy(
                        "Optional - leave blank to stay anonymous"
                    )
                }
            ),
        }