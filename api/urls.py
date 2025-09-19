# from django.urls import path 
# from . import views

# from rest_framework.routers import DefaultRouter
# from .views import UserViewSet , RegisterView , ContractViewSet

# router = DefaultRouter()
# router.register(r'users', UserViewSet)
# router.register(r'contracts', ContractViewSet, basename='contract')
# urlpatterns = router.urls

# from .models import *



# router = DefaultRouter()
# router.register(r'users', UserViewSet)

# urlpatterns = router.urls



# # urlpatterns = [
# #     path('users/' , views.get_all_users , name='users'),
# #     path('users_filters/' , views.get_filter_users , name='filtered_users'),
# #     path("users/create/", views.create_user, name="create_user"),  # POST
# #     path('users/<str:pk>/' , views.users_list_id , name='users_list'),
# #     path("users/<int:user_id>/assign-rank/<int:rank_id>/", views.assign_rank, name="assign_rank"),
# # ]


# urlpatterns = [
#     # --- List and Filter Views ---
#     # It's good practice to add trailing slashes to all endpoints for consistency.

#         # Add the new registration path
#     path('register/', RegisterView.as_view(), name='api_register'),

#     path('users/', views.get_all_users, name='users_list'),
#     path('users/filter/', views.get_filter_users, name='filtered_users'),

#     # --- Create View ---
#     path("users/create/", views.create_user, name="create_user"),

#     # --- Detail, Update, and Delete View ---
#     # The fix is to add a trailing slash here: <str:pk>/
#     path('users/<str:pk>/', views.user_detail, name='user_detail'),

#     # --- Other Actions ---
#     path("users/<int:user_id>/assign-rank/<int:rank_id>/", views.assign_rank, name="assign_rank"),
# ]


from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    RegisterView,
    ContractViewSet,
    ReferenceViewSet,
    SeaServiceViewSet,
    CertificateViewSet,
    RankViewSet,
    get_all_users,
    create_user,
    get_filter_users,
    user_detail,
    assign_rank,
    get_user_certificates,
    get_user_ranks,
    add_user_certificate,
    add_user_rank,
    remove_user_certificate,
    remove_user_rank,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="user")
router.register(r'contracts', ContractViewSet, basename="contract")
router.register(r'references', ReferenceViewSet, basename="reference")
router.register(r'sea-services', SeaServiceViewSet, basename="seaservice")
router.register(r'certificates', CertificateViewSet, basename="certificate")
router.register(r'ranks', RankViewSet, basename="rank")

urlpatterns = [
    path('', include(router.urls)),
    path('register/', RegisterView.as_view(), name='register'),
    path('all/', get_all_users, name='get_all_users'),
    path('create/', create_user, name='create_user'),
    path('filter/', get_filter_users, name='get_filter_users'),
    path('users/<int:pk>/', user_detail, name='user-detail'),
    path('users/<int:user_id>/assign-rank/<int:rank_id>/', assign_rank, name='assign-rank'),
    
    # User-specific certificate and rank endpoints
    path('users/<int:user_id>/certificates/', get_user_certificates, name='user-certificates'),
    path('users/<int:user_id>/ranks/', get_user_ranks, name='user-ranks'),
    path('users/<int:user_id>/certificates/add/', add_user_certificate, name='add-user-certificate'),
    path('users/<int:user_id>/ranks/add/', add_user_rank, name='add-user-rank'),
    path('users/<int:user_id>/certificates/<int:certificate_id>/remove/', remove_user_certificate, name='remove-user-certificate'),
    path('users/<int:user_id>/ranks/<int:rank_id>/remove/', remove_user_rank, name='remove-user-rank'),
]

