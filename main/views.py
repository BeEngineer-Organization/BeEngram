from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.db.models import Case, Count, Q, When
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .forms import (
    CommentForm,
    ConfirmForm,
    PostForm,
    ProfileEditForm,
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
        self.object = user
        user.is_active = False
        user.save()
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
        to_email = form.cleaned_data.get("email")
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
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

    def get(self, request, *args, **kwargs):
        self.queryset = User.objects.filter(pk=kwargs["pk"]).prefetch_related("posts", "like").annotate(
            Count("posts", distinct=True),
            Count("follow", distinct=True),
            Count("followed", distinct=True),
        )
        return super().get(self, request, *args, **kwargs)


class FollowListView(LoginRequiredMixin, ListView):
    model = User
    template_name = "main/follow_list.html"
    paginate_by = 20
    
    def get(self, request, *args, **kwargs):
        self.user_id = kwargs["pk"]
        user = get_object_or_404(User, pk=kwargs["pk"])
        follow_list = user.follow.all()
        if "followed" in self.request.GET:
            self.queryset = (
                user.followed
                .annotate(
                    is_follow=Case(
                        When(followed__id__contains=request.user.pk, then=True),
                        default=False
                    )
                )
            )
        else:
            self.queryset = (
                follow_list
                .annotate(
                    is_follow=Case(
                        When(followed__id__contains=request.user.pk, then=True),
                        default=False
                    )
                )
            )

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = request.user
        target = get_object_or_404(User, pk=request.POST["target"])
        if "follow" in request.POST:
            user.follow.add(target)
            user.save()
        elif "unfollow" in request.POST:
            user.follow.remove(target)
            user.save()
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_id"] = self.user_id
        return context

