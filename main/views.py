from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Case, Count, Q, When
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .forms import (
    CommentForm,
    ConfirmForm,
    PostForm,
    ProfileEditForm,
    SearchForm,
    SignUpForm,
)
from .models import Comment, Post
from .tokens import account_activation_token

User = get_user_model()


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    ordering = ("-post_date",)
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related("user")
        if "follow" in self.request.GET:
            queryset = queryset.filter(
                Q(user=self.request.user)
                | Q(user__in=self.request.user.follow.all())
            )
        return queryset


class SignUpView(CreateView):
    template_name = "registration/signup.html"
    success_url = reverse_lazy("signup_email_send")
    form_class = SignUpForm

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        self.object = user

        current_site = get_current_site(self.request)
        mail_subject = "[BeEngram] アカウントを有効化してください"
        message = render_to_string(
            "registration/signup_email.html",
            {
                "user": user,
                "domain": current_site.domain,
                "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                "token": account_activation_token.make_token(user),
            },
        )
        user.email_user(mail_subject, message)
        return HttpResponseRedirect(self.get_success_url())


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("home")
    else:
        return HttpResponse("このリンクは無効です。申し訳ありませんが、もう一度登録の処理をやり直してください。")


class PostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    form_class = ConfirmForm
    success_url = reverse_lazy("home")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user")
            .prefetch_related("comments")
        )


class CommentView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm
    success_url = reverse_lazy("home")

    def get_form_kwargs(self):
        post = get_object_or_404(Post, pk=self.kwargs["post_pk"])
        self.object = self.model(user=self.request.user, post=post)
        return super().get_form_kwargs()


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = "main/edit_profile.html"
    model = User
    form_class = ProfileEditForm
    success_url = reverse_lazy("settings")

    def get_object(self, queryset=None):
        return self.request.user


class ProfileView(LoginRequiredMixin, DetailView):
    model = User

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("posts", "like")
            .annotate(
                Count("posts", distinct=True),
                Count("follow", distinct=True),
                Count("followed", distinct=True),
            )
        )


class FollowMixin:
    def post(self, request, *args, **kwargs):
        target = get_object_or_404(User, pk=self.request.POST.get("target", 0))
        if "follow" in self.request.POST:
            self.request.user.follow.add(target)
        elif "unfollow" in self.request.POST:
            self.request.user.follow.remove(target)
        return HttpResponseRedirect(self.request.META.get("HTTP_REFERER"))


class FollowListView(LoginRequiredMixin, FollowMixin, ListView):
    template_name = "main/follow_list.html"
    ordering = ("username",)

    def get_queryset(self):
        user = get_object_or_404(User, pk=self.kwargs["pk"])
        if "followed" in self.request.GET:
            queryset = user.followed
        else:
            queryset = user.follow
        self.queryset = queryset.annotate(
            is_follow=Case(
                When(followed__id__contains=self.request.user.pk, then=True),
                default=False,
            )
        )

        return super().get_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_id"] = self.kwargs["pk"]
        return context


class SearchView(LoginRequiredMixin, FollowMixin, ListView):
    template_name = "main/search.html"

    def get_queryset(self):
        form = SearchForm(self.request.GET)
        if form.is_valid():
            keyword = form.cleaned_data["keyword"]
            if "post" in self.request.GET:
                self.queryset = self._search_posts(keyword)
            else:
                self.queryset = self._search_users(keyword)
        else:
            if "post" in self.request.GET:
                self.queryset = Post.objects.none()
            else:
                self.queryset = User.objects.none()

        return super().get_queryset()

    def _search_posts(self, keyword):
        queryset = Post.objects.all().select_related("user")
        for word in keyword.split():
            queryset = queryset.filter(note__icontains=word)
        return queryset

    def _search_users(self, keyword):
        queryset = User.objects.all().annotate(
            is_follow=Case(
                When(followed__id__contains=self.request.user.pk, then=True),
                default=False,
            )
        )
        for word in keyword.split():
            queryset = queryset.filter(username__icontains=word)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "keyword" in self.request.GET:
            context["form"] = SearchForm(self.request.GET)
        else:
            context["form"] = SearchForm()
        return context


class PostLikeAPIView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            post = Post.objects.get(pk=self.kwargs["pk"])
            if post in self.request.user.like.all():
                self.request.user.like.remove(post)
            else:
                self.request.user.like.add(post)
            result = "success"
        except Post.DoesNotExist:
            result = "DoesNotExist"
        return JsonResponse({"result": result})
