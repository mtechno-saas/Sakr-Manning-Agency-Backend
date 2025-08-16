from django.urls import path 
from . import views

urlpatterns = [
    path('users/' , views.get_all_users , name='users'),
    path('users_filters/' , views.get_filter_users , name='filtered_users'),
    path("users/create/", views.create_user, name="create_user"),  # POST
    path('users/<str:pk>/' , views.users_list_id , name='users_list'),
]
