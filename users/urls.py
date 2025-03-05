from django.urls import path
from . import views

urlpatterns = [
    path("profile/", views.UserDetailView.as_view(), name="user-detail"),
]