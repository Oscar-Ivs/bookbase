from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import logout_view

urlpatterns = [
    # Authentication routes
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),

    # Core pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('collection/', views.my_collection, name='my_collection'),
    path('profile/', views.profile, name='profile'),

    # Book actions
    path('add/', views.add_book, name='add_book'),
    path('book/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('book/<int:book_id>/delete/', views.delete_book, name='delete_book'),

    # Google Books API search
    path('search_google_books/', views.search_google_books, name='search_google_books'),

    # AJAX endpoint to fetch books for homepage
    path('get_books/', views.fetch_books, name='fetch_books'),

]

# This file defines all URL patterns for the 'books' app,
# including authentication, core views, book management, and search.
