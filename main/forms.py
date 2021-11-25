from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Post, User


class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email")


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("img", "note")
        widgets = {
            "img": forms.FileInput(
                attrs={
                    "accept": "image/jpeg,image/png",
                    "data-form-image": True,
                }
            ),
            "note": forms.Textarea(
                attrs={"placeholder": "説明文（300字以内）", "rows": 7}
            ),
        }


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("icon", "username", "profile")
        widgets = {
            "icon": forms.FileInput(
                attrs={
                    "accept": "image/jpeg,image/png",
                    "data-form-image": True,
                }
            ),
            "profile": forms.Textarea(
                attrs={"placeholder": "150字以内", "rows": 7}
            ),
        }


class ConfirmForm(forms.Form):
    confirm = forms.BooleanField(required=True)


class SearchForm(forms.Form):
    keyword = forms.CharField(
        label="検索",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "検索"}),
    )
