from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import Comment, Post, User


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=200, help_text='Required')
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("img", "note")
        widgets = {
            "img": forms.FileInput(attrs={"accept": "image/jpeg,image/png", "data-form-image": True}),
            "note": forms.Textarea(attrs={"placeholder": "説明文", "rows": 7}),
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('icon', 'username', 'profile')
        widgets = {
            "icon": forms.FileInput(attrs={"accept": "image/jpeg,image/png"}),
        }

