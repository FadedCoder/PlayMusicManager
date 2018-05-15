from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Music


class SignUpForm(UserCreationForm):
    oauth_code = forms.CharField(max_length=100, help_text='Enter OAuth code here.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'oauth_code')


class MusicUploadForm(forms.ModelForm):
    music_file = forms.FileField()

    class Meta:
        model = Music
        fields = ('music_file', 'title', 'album', 'composer', 'genre', 'language',
                  'artist', 'album_artist',)
