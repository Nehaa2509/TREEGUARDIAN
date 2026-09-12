"""
apps/users/urls.py

URL patterns for the users app.
These are included under /api/auth/ in config/urls.py.

So the full paths become:
    /api/auth/register/
    /api/auth/login/
    /api/auth/logout/
    /api/auth/profile/
"""

from django.urls import path
from .views import RegisterView, LoginView, LogoutView, ProfileView

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/",    LoginView.as_view(),    name="login"),
    path("logout/",   LogoutView.as_view(),   name="logout"),
    path("profile/",  ProfileView.as_view(),  name="profile"),
]
