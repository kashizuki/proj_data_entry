from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Activity, Project, Work


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Email atau Username",
        widget=forms.TextInput(attrs={"placeholder": "Email atau username"}),
    )


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    nim = forms.CharField(max_length=20, required=True)

    class Meta:
        model = User
        fields = ("username", "email", "nim", "password1", "password2")


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "name",
            "description",
            "location",
            "start_date",
            "end_date",
            "executor",
            "supervisor",
        ]


class WorkForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = [
            "name",
            "description",
            "location",
            "start_date",
            "end_date",
            "executor",
            "supervisor",
            "category",
        ]


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ["name", "execution_time", "executor"]

