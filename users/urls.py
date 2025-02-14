from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.UserRegisterView.as_view(), name="user-register"),
    path("profile/", views.UserDetailView.as_view(), name="user-detail"),
]

# POST /register/ → User registration
# GET/PUT /profile/ → View & update user profile