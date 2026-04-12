from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path("auth/", views.auth_view, name="auth"),
    path("logout/", views.logout_view, name="logout"),
]
