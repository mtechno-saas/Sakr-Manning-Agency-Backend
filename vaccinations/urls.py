from rest_framework.routers import DefaultRouter
from .views import VaccinationViewSet

router = DefaultRouter()
router.register("vaccinations", VaccinationViewSet, basename="vaccination")

urlpatterns = router.urls
