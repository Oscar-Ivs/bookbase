from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import logout_view

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('collection/', views.my_collection, name='my_collection'),
    path('profile/', views.profile, name='profile'),
    path('add/', views.add_book, name='add_book'),
    path('book/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('book/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('api/search-books/', views.google_books_search, name='google_books_search'),
    path('search_google_books/', views.search_google_books, name='search_google_books'),


]
# This file defines URL patterns for the 'books' app, including user registration and authentication views.
# The 'register' view is for user registration, while 'login' and 'logout'