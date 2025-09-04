# books/forms.py
from django import forms
from .models import Book, Profile
from django.contrib.auth.models import User


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "author", "description", "cover_url", "status", "notes"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        # IMPORTANT: do NOT include is_public here
        fields = ["bio", "avatar"]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }
