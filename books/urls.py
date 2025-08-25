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

    # Unified book detail view (works for DB + API IDs)
    path("books/<book_id>/", views.book_detail, name="book_detail"),

    # Community features
    path("community/", views.community_list, name="community_list"),
    path("community/<str:username>/", views.community_profile, name="community_profile"),

    # Password management
    path('password_change/', auth_views.PasswordChangeView.as_view(
        template_name='registration/password_change_form.html'), name='password_change'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='registration/password_change_done.html'), name='password_change_done'),

    # Comment and notification routes
    path('comments/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('notifications/mark-all-read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    
]

# This file defines all URL patterns for the 'books' app,
# including authentication, core views, book management, 
# search, community features, and password management.
