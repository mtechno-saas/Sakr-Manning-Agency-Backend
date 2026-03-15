from django.urls import path
from .views import GenerateContractView, ListGeneratedContractsView

urlpatterns = [
    path('generate/<int:user_id>/', GenerateContractView.as_view(), name='generate_contract'),
    path('list/', ListGeneratedContractsView.as_view(), name='list_contracts'),
]
