from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", login_required(views.IndexView.as_view()), name="index"),
    path("top", TemplateView.as_view(template_name='main/top.html'), name="top"),
    path("login", LoginView.as_view(), name="login"),
    path("signup", views.SignUpView.as_view(), name="signup"),
    path("signup_email_send", TemplateView.as_view(template_name='registration/signup_email_send.html'), name="signup_email_send"),
    path("activate/<uidb64>/<token>/", views.activate, name='activate'),
]
