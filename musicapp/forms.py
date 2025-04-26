from django import forms
from django.contrib.auth.forms import SetPasswordForm
from .models import Playlist, PlaylistSong

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email Address", max_length=254)
    
class CustomSetPasswordForm(SetPasswordForm):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput,
        label=("New Password"),
        help_text=("Your new password must contain at least 8 characters."),
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput,
        label=("Confirm Password"),
        help_text=("Enter the same password as before, for verification."),
    )


class PasswordChangeForm(forms.Form):
    Old_Password = forms.CharField(
        widget=forms.PasswordInput,
        label=("Old Password"),
        help_text=("Your old password must contain at least 8 characters."),
    )

    New_Password = forms.CharField(
        widget=forms.PasswordInput,
        label=("New Password"),
        help_text=("Your new password must contain at least 8 characters."),
    )

class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['name']