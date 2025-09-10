from django.urls import path 
from . import views

from rest_framework.routers import DefaultRouter
from .views import UserViewSet , RegisterView , ContractViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'contracts', ContractViewSet, basename='contract')
urlpatterns = router.urls

from .models import *



router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = router.urls



# urlpatterns = [
#     path('users/' , views.get_all_users , name='users'),
#     path('users_filters/' , views.get_filter_users , name='filtered_users'),
#     path("users/create/", views.create_user, name="create_user"),  # POST
#     path('users/<str:pk>/' , views.users_list_id , name='users_list'),
#     path("users/<int:user_id>/assign-rank/<int:rank_id>/", views.assign_rank, name="assign_rank"),
# ]


urlpatterns = [
    # --- List and Filter Views ---
    # It's good practice to add trailing slashes to all endpoints for consistency.

        # Add the new registration path
    path('register/', RegisterView.as_view(), name='api_register'),

    path('users/', views.get_all_users, name='users_list'),
    path('users/filter/', views.get_filter_users, name='filtered_users'),

    # --- Create View ---
    path("users/create/", views.create_user, name="create_user"),

    # --- Detail, Update, and Delete View ---
    # The fix is to add a trailing slash here: <str:pk>/
    path('users/<str:pk>/', views.user_detail, name='user_detail'),

    # --- Other Actions ---
    path("users/<int:user_id>/assign-rank/<int:rank_id>/", views.assign_rank, name="assign_rank"),
]