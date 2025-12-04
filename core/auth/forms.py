from typing import Any

from django import forms
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from core.models import User


class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=250, label="First Name", required=True)
    last_name = forms.CharField(max_length=250, label="Last Name", required=True)

    def clean_first_name(self) -> Any:
        first_name = self.cleaned_data.get("first_name", "").strip()
        if not first_name:
            raise forms.ValidationError(_("First name is required."), code="required")
        return first_name

    def clean_last_name(self) -> Any:
        last_name = self.cleaned_data.get("last_name", "").strip()
        if not last_name:
            raise forms.ValidationError(_("Last name is required."), code="required")
        return last_name

    def signup(self, request: HttpRequest, user: User) -> User:
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.save()
        return user
