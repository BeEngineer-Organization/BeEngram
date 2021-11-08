import django.contrib.auth.views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path(
        "", TemplateView.as_view(template_name="main/index.html"), name="index"
    ),
    path("home/", views.PostListView.as_view(), name="home"),
    path(
        "settings/",
        TemplateView.as_view(template_name="main/settings.html"),
        name="settings",
    ),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path(
        "signup_email_send/",
        TemplateView.as_view(
            template_name="registration/signup_email_send.html"
        ),
        name="signup_email_send",
    ),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("post/<pk>", views.PostDetailView.as_view(), name="post_detail"),
    path("post/", views.PostView.as_view(), name="new_post"),
    path(
        "delete_post/<pk>", views.PostDeleteView.as_view(), name="delete_post"
    ),
    path("comment/<post_pk>/", views.CommentView.as_view(), name="comment"),
    path("profile/<int:pk>", views.ProfileView.as_view(), name="profile"),
    path(
        "edit_profile/<int:pk>",
        views.ProfileEditView.as_view(),
        name="edit_profile",
    ),
]
