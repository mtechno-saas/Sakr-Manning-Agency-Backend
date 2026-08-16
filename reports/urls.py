from django.urls import path

from .views import ReportsDropdownOptionsView, ReportsGenerateView

app_name = "reports"

urlpatterns = [
    # POST/GET a filter spec, get a generated report back.
    path(
        "generate/",
        ReportsGenerateView.as_view(),
        name="generate",
    ),
    # GET all dropdown options for the Reports page UI.
    path(
        "dropdown-options/",
        ReportsDropdownOptionsView.as_view(),
        name="dropdown-options",
    ),
]
