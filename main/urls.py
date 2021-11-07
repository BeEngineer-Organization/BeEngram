from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("top", TemplateView.as_view(template_name='main/top.html'), name="top"),
    path("settings", TemplateView.as_view(template_name='main/settings.html'), name="settings"),
    path("login", LoginView.as_view(), name="login"),
    path("logout", LogoutView.as_view(), name="logout"),
    path("edit_profile/<int:pk>", views.ProfileEditView.as_view(), name="edit_profile"),
    path("signup", views.SignUpView.as_view(), name="signup"),
    path("signup_email_send", TemplateView.as_view(template_name="registration/signup_email_send.html"), name="signup_email_send"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("post/", views.PostView.as_view(), name="new_post"),
]
