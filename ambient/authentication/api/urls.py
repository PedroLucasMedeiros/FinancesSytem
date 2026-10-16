# authentication/urls.py
from django.urls import path
from .views import LogoutView, MeView, RegisterView, StatusView

app_name = "authentication"

urlpatterns = [
    path("status/", StatusView.as_view(), name="status"),
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("logout/", LogoutView.as_view(), name="logout"),
]