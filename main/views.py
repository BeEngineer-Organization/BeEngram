from django.contrib.auth import get_user_model, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView

from .forms import LoginForm, PostForm, SignUpForm
from .models import Comment, Post
from .tokens import account_activation_token

User = get_user_model()


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = "main/index.html"


class SignUpView(CreateView):
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('signup_email_send')
    form_class = SignUpForm

    def form_valid(self, form):
        result = super().form_valid(form)
        user = form.save(commit=False)
        user.is_active = False
        user.save()
        current_site = get_current_site(self.request)
        mail_subject = '[BeEngram] アカウントを有効化してください'
        message = render_to_string('registration/signup_email.html', {
            'user': user,
            'domain': current_site.domain,
            'uid':urlsafe_base64_encode(force_bytes(user.pk)),
            'token':account_activation_token.make_token(user),
        })
        to_email = form.cleaned_data.get('email')
        email = EmailMessage(mail_subject, message, to=[to_email])
        email.send()
        return result


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
        return redirect("index")
    else:
        return HttpResponse("このリンクは無効です。申し訳ありませんが、もう一度登録の処理をやり直してください。")


class PostView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())
