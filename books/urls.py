from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),  # <-- final version
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('collection/', views.my_collection, name='my_collection'),
    path('profile/', views.profile, name='profile'),
]
# This file defines URL patterns for the 'books' app, including user registration and authentication views.
# The 'register' view is for user registration, while 'login' and 'logout'