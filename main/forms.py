from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User, Post, Comment

class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class LoginForm(AuthenticationForm):
    pass