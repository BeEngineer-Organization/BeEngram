from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Case, Q, When
from django.http import (
    HttpResponseRedirect,
    JsonResponse,
)
from django.urls import reverse_lazy
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView

from .forms import (
    ConfirmForm,
    PostForm,
    ProfileEditForm,
    SearchForm,
    SignUpForm,
)
from .models import Post

User = get_user_model()


class PostListView(LoginRequiredMixin, ListView):
    model = Post
    ordering = ("-post_date",)
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related("user")
        if "follow" in self.request.GET:
            queryset = queryset.filter(
                Q(user=self.request.user) | Q(user__in=self.request.user.follow.all())
            )
        return queryset


class SignUpView(CreateView):
    template_name = "registration/signup.html"
    success_url = reverse_lazy("home")
    form_class = SignUpForm

    def form_valid(self, form):
        response = super().form_valid(form)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return response


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
    pk_url_kwarg = "id"

    def get_queryset(self):
        return super().get_queryset().select_related("user")


class ProfileEditView(LoginRequiredMixin, UpdateView):
    template_name = "main/edit_profile.html"
    model = User
    form_class = ProfileEditForm
    success_url = reverse_lazy("settings")

    def get_object(self, queryset=None):
        return self.request.user


class SearchView(LoginRequiredMixin, ListView):
    template_name = "main/search.html"
    paginate_by = 20

    def get_queryset(self):
        form = SearchForm(self.request.GET)
        if form.is_valid():
            keyword = form.cleaned_data["keyword"]
            if "post" in self.request.GET:
                queryset = self._search_posts(keyword)
            else:
                queryset = self._search_users(keyword)
        else:
            if "post" in self.request.GET:
                queryset = Post.objects.none()
            else:
                queryset = User.objects.none()
        return queryset

    def _search_posts(self, keyword):
        queryset = Post.objects.all().select_related("user")

        for word in keyword.split():
            queryset = queryset.filter(note__icontains=word)
        return queryset.order_by("-post_date")

    def _search_users(self, keyword):
        follow_list = self.request.user.follow.all().values_list("id", flat=True)
        queryset = User.objects.all().annotate(
            is_follow=Case(
                When(id__in=follow_list, then=True),
                default=False,
            )
        )

        for word in keyword.split():
            queryset = queryset.filter(username__icontains=word)
        return queryset.order_by("-is_follow", "username")

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
            post = Post.objects.get(id=self.kwargs["id"])
            if post in self.request.user.like.all():
                self.request.user.like.remove(post)
            else:
                self.request.user.like.add(post)
            result = "success"
        except Post.DoesNotExist:
            result = "DoesNotExist"
        return JsonResponse({"result": result})
