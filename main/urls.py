import django.contrib.auth.views as auth_views
from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path("", TemplateView.as_view(template_name="main/index.html"), name="index"),
    path("home/", views.PostListView.as_view(), name="home"),
    path(
        "settings/",
        TemplateView.as_view(template_name="main/settings.html"),
        name="settings",
    ),
    path("login/", auth_views.LoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("post/<int:id>", views.PostDetailView.as_view(), name="post_detail"),
    path("post/", views.PostView.as_view(), name="new_post"),
    path(
        "delete_post/<int:id>",
        views.PostDeleteView.as_view(),
        name="delete_post",
    ),
    path(
        "edit_profile/<int:id>",
        views.ProfileEditView.as_view(),
        name="edit_profile",
    ),
    path("search/", views.SearchView.as_view(), name="search"),
    path("like/<int:id>", views.PostLikeAPIView.as_view(), name="like"),
]
