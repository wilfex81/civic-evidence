from django.contrib import admin

from .models import Observation, Project


class ObservationInline(admin.TabularInline):
    model = Observation
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "official_status", "official_status_date", "location")
    list_filter = ("official_status", "is_demo_data")
    search_fields = ("name", "location", "responsible_organization")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ObservationInline]


@admin.register(Observation)
class ObservationAdmin(admin.ModelAdmin):
    list_display = ("project", "date_observed", "status", "evidence_type")
    list_filter = ("status", "evidence_type")
