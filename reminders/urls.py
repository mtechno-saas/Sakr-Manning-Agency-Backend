"""URL config for the Reminders app — full CRUD via DefaultRouter."""
from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "reminders"

router = DefaultRouter()
router.register(r'', views.ReminderViewSet, basename='reminder')

urlpatterns = router.urls

# Note: the URL is just /api/reminders/ (no trailing resource). The router
# adds /<id>/ for retrieve/update/delete automatically, and the custom
# actions add /upcoming/, /overdue/, /<id>/mark_done/, /<id>/mark_pending/.
