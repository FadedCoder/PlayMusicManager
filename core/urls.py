from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.registration, name='registration'),
    path('login/', auth_views.login, {'template_name': 'core/login.html'}, name='login'),
    path('logout/', auth_views.logout, name='logout'),
    path('upload/', views.upload, name='upload'),
    path('youtube/', views.youtube_upload, name='youtube_upload'),
]
