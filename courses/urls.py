from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, download_course_document

router = DefaultRouter()
router.register(r'courses', CourseViewSet)

urlpatterns = [
    # Router handles: GET list, POST create, GET detail, DELETE
    path('', include(router.urls)),
    
    # Custom path for the download function
    path('courses/<int:course_id>/download/', download_course_document, name='course-download'),
]
