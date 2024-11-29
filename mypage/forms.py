
from django import forms


class ProfileUpdateForm(forms.Form):
    bank = forms.CharField(max_length=100, required=True, label="Bank")
    address = forms.CharField(max_length=255, required=True, label="Address")


class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="Current Password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        required=True,
        label="New Password"
    )
