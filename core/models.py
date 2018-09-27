from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from oauth2client.contrib.django_util.models import CredentialsField


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    google_oauth = CredentialsField()
    default_title = models.CharField(max_length=100, blank=True)
    default_album = models.CharField(max_length=100, blank=True)
    default_composer = models.CharField(max_length=100, blank=True)
    default_genre = models.CharField(max_length=100, blank=True)
    default_language = models.CharField(max_length=100, blank=True)
    default_artist = models.CharField(max_length=100, blank=True)
    default_album_artist = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()


class Music(models.Model):
    play_id = models.CharField(max_length=50, blank=True)
    title = models.CharField(max_length=100, blank=True)
    album = models.CharField(max_length=100, blank=True)
    composer = models.CharField(max_length=100, blank=True)
    genre = models.CharField(max_length=100, blank=True)
    language = models.CharField(max_length=100, blank=True)
    artist = models.CharField(max_length=100, blank=True)
    album_artist = models.CharField(max_length=100, blank=True)
