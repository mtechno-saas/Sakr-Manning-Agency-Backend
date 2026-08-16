from django.urls import path

from .views import ReportsGenerateView

app_name = "reports"

urlpatterns = [
    # POST a filter spec, get a generated report back.
    # We mount at /api/reports/generate/ — see saker/urls.py for the
    # include() that wires the prefix.
    path(
        "generate/",
        ReportsGenerateView.as_view(),
        name="generate",
    ),
]
