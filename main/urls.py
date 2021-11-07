from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("signup", views.SignUpView.as_view(), name="signup"),
    path("signup_email_send", TemplateView.as_view(template_name='registration/signup_email_send.html'), name="signup_email_send"),
    path("activate/<uidb64>/<token>/", views.activate, name='activate'),
]
