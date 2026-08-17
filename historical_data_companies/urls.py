from django.urls import path

from .views import HistoricalDataForCompaniesView

app_name = "historical_data_companies"

urlpatterns = [
    # One big endpoint that returns every analysis section in one
    # response. See HistoricalDataForCompaniesView for the contract.
    path(
        "",
        HistoricalDataForCompaniesView.as_view(),
        name="analyze",
    ),
]
