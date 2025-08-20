# books/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from .models import Book, Profile
from .forms import BookForm, ProfileForm, UserUpdateForm
import requests
import os
from PIL import Image
from django.utils import timezone


# User registration view
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


# Homepage view
def home(request):
    return render(request, 'home.html')


# About page view
def about(request):
    return render(request, 'about.html')


# Profile view with avatar replacement, default protection, and image compression
@login_required
def profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    profile_form = ProfileForm(request.POST or None, request.FILES or None, instance=profile)
    user_form = UserUpdateForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        # Handle avatar or bio
        if 'bio' in request.POST or 'avatar' in request.FILES:
            if profile_form.is_valid():
                # Delete old avatar if uploading a new one (and it's not placeholder)
                if 'avatar' in request.FILES and profile.avatar:
                    old_path = profile.avatar.path
                    if os.path.isfile(old_path) and not profile.avatar.name.endswith("avatar-placeholder.png"):
                        os.remove(old_path)

                profile_form.save()

                # Resize uploaded avatar
                if 'avatar' in request.FILES:
                    avatar_path = profile.avatar.path
                    try:
                        img = Image.open(avatar_path)
                        img = img.convert('RGB')
                        img.thumbnail((300, 300))  # Resize to max 300x300
                        img.save(avatar_path, format='JPEG', quality=85)
                    except Exception as e:
                        print("Image resize error:", e)

                return redirect('profile')

        # Handle username/email
        elif 'update_user_form' in request.POST:
            if user_form.is_valid():
                user_form.save()
                return redirect('profile')

    # Book stats for display
    books = Book.objects.filter(user=request.user)
    read_count = books.filter(status='read').count()
    unread_count = books.filter(status='unread').count()
    total_books = books.count()

    context = {
        'profile': profile,
        'form': profile_form,
        'user_form': user_form,
        'read_count': read_count,
        'unread_count': unread_count,
        'total_books': total_books,
        'bio_background': '#acbdd8',
    }
    return render(request, 'profile.html', context)


# Custom logout view using GET
def logout_view(request):
    logout(request)
    return redirect('home')


# My Collection view — shows books owned by the logged-in user
@login_required
def my_collection(request):
    books = Book.objects.filter(user=request.user).order_by('title')
    return render(request, 'my_collection.html', {'books': books})


# Add a book to the collection
@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            new_book = form.save(commit=False)
            new_book.user = request.user
            new_book.save()
            return redirect('my_collection')
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})


# Edit an existing book
@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('my_collection')
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_book.html', {'form': form, 'book': book})


# Delete a book
@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    if request.method == 'POST':
        book.delete()
        return redirect('my_collection')
    return render(request, 'delete_book.html', {'book': book})


# AJAX view for form auto-fill — searches Google Books by title
def search_google_books(request):
    query = request.GET.get('q', '')
    start_index = int(request.GET.get('startIndex', 0))
    max_results = int(request.GET.get('maxResults', 6))  # default 6 per batch

    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)

    # Correct API request with startIndex + maxResults + full description
    url = (
        f'https://www.googleapis.com/books/v1/volumes'
        f'?q={query}&startIndex={start_index}&maxResults={max_results}&projection=full'
    )

    try:
        response = requests.get(url)
        data = response.json()
        books = []

        for item in data.get('items', []):
            info = item.get('volumeInfo', {})
            books.append({
                'title': info.get('title', ''),
                'author': ', '.join(info.get('authors', [])) if 'authors' in info else '',
                'description': info.get('description', ''),  # ✅ full description
                'cover_url': info.get('imageLinks', {}).get('thumbnail', ''),
            })

        return JsonResponse({'books': books})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# Build the Google Books API request URL for homepage browsing
def fetch_books(request):
    query = request.GET.get('q', 'fiction')
    order = request.GET.get('order', 'relevance')
    start_index = int(request.GET.get('startIndex', 0))
    max_results = 24  # Load 24 books per batch

    url = (
        f"https://www.googleapis.com/books/v1/volumes?"
        f"q={query}&orderBy={order}&startIndex={start_index}&maxResults={max_results}"
    )

    try:
        response = requests.get(url)
        data = response.json()
        books = []

        for item in data.get('items', []):
            volume = item.get('volumeInfo', {})
            books.append({
                'title': volume.get('title', 'Untitled'),
                'author': ', '.join(volume.get('authors', [])),
                'description': volume.get('description', '')[:300],
                'thumbnail': volume.get('imageLinks', {}).get('thumbnail', ''),
            })

        return JsonResponse({'books': books})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def book_detail(request, book_id):
    """
    Show a single book with: cover + status (left), description (middle), notes (right).
    Only the owner can view their book.
    """
    book = get_object_or_404(Book, id=book_id, user=request.user)

    context = {
        "book": book,
        "added_when": getattr(book, "created_at", None) or getattr(book, "added_at", None) or None,  # optional
    }
    return render(request, 'book_detail.html', context)

# Detail page for Google Books API results
def book_api_detail(request, book_id):
    """
    Fetch a book by ID from Google Books API and display details
    using the same book_detail.html template.
    """
    import requests
    api_url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    response = requests.get(api_url)

    if response.status_code != 200:
        return render(request, "book_detail.html", {
            "book": {
                "title": "Book not found",
                "description": "Unable to fetch data.",
                "cover_url": "/static/img/book-placeholder.png",
            }
        })

    data = response.json().get("volumeInfo", {})

    # Normalize so template works the same for DB + API books
    book = {
        "title": data.get("title", "No title"),
        "author": ", ".join(data.get("authors", [])),
        "description": data.get("description", "No description available."),
        "cover_url": data.get("imageLinks", {}).get("thumbnail", "/static/img/book-placeholder.png"),
        "publisher": data.get("publisher", "Unknown"),
        "publishedDate": data.get("publishedDate", "N/A"),
        "pageCount": data.get("pageCount", "N/A"),
    }

    return render(request, "book_detail.html", {"book": book})
