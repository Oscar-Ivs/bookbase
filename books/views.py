# books/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Book
from .forms import BookForm
from django.shortcuts import get_object_or_404


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


# Profile page view
@login_required
def profile(request):
    return render(request, 'profile.html')


# Custom logout view using GET
def logout_view(request):
    logout(request)
    return redirect('home')


# My Collection view — shows books owned by the logged-in user
@login_required
def my_collection(request):
    books = Book.objects.filter(user=request.user).order_by('title')
    return render(request, 'my_collection.html', {'books': books})


# Add a book form to the collection
@login_required
def add_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            new_book = form.save(commit=False)
            new_book.user = request.user  # assign current user
            new_book.save()
            return redirect('my_collection')
    else:
        form = BookForm()
    return render(request, 'add_book.html', {'form': form})


# Edit a book (only allowed if current user owns it)
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

# Delete a book (only allowed if current user owns it)
@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)

    if request.method == 'POST':
        book.delete()
        return redirect('my_collection')

    return render(request, 'delete_book.html', {'book': book})

# Delete book placeholder
@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)

    if request.method == 'POST':
        book.delete()
        return redirect('my_collection')

    return render(request, 'delete_book.html', {'book': book})

# AJAX view to search Google Books API
import requests
from django.http import JsonResponse

# AJAX view to search Google Books
@login_required
def google_books_search(request):
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'items': []})

    url = 'https://www.googleapis.com/books/v1/volumes'
    params = {
        'q': query,
        'maxResults': 5,
    }

    response = requests.get(url, params=params)
    data = response.json()

    results = []
    for item in data.get('items', []):
        volume = item.get('volumeInfo', {})
        results.append({
            'title': volume.get('title', ''),
            'authors': ', '.join(volume.get('authors', [])),
            'description': volume.get('description', ''),
            'thumbnail': volume.get('imageLinks', {}).get('thumbnail', ''),
        })

    return JsonResponse({'items': results})

import requests
from django.http import JsonResponse

# Google Books API search view
@login_required
def search_google_books(request):
    query = request.GET.get('q')
    if not query:
        return JsonResponse({'books': []})

    response = requests.get('https://www.googleapis.com/books/v1/volumes', params={
        'q': query,
        'maxResults': 6,
    })

    results = []
    if response.status_code == 200:
        data = response.json()
        for item in data.get('items', []):
            volume = item['volumeInfo']
            results.append({
                'title': volume.get('title', ''),
                'author': ', '.join(volume.get('authors', ['Unknown'])),
                'description': volume.get('description', '')[:300],
                'cover_url': volume.get('imageLinks', {}).get('thumbnail', ''),
            })

    return JsonResponse({'books': results})


