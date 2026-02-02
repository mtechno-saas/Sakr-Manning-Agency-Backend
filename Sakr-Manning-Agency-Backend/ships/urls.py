from rest_framework.routers import DefaultRouter
from .views import ShipViewSet

router = DefaultRouter()
router.register(r'', ShipViewSet)  # base path /api/ships/

urlpatterns = router.urls
