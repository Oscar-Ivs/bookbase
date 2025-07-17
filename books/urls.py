from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
]
# This file defines URL patterns for the 'books' app, including user registration and authentication views.
# The 'register' view is for user registration, while 'login' and 'logout' views are provided by Django's built-in authentication system.

