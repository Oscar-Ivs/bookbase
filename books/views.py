# books/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Book
from .forms import BookForm
import requests


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


# View to fetch books from the Google Books API
def fetch_books(request):
    # Get optional query params (default to 'fiction' and 'relevance')
    query = request.GET.get('q', 'fiction')
    order = request.GET.get('order', 'relevance')  # or 'newest'
    max_results = 20

    # Build the Google Books API request URL
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&orderBy={order}&maxResults={max_results}"

    try:
        # Send GET request to Google Books API
        response = requests.get(url)
        data = response.json()
        books = []

        # Extract key fields from each book in the response
        for item in data.get('items', []):
            volume = item.get('volumeInfo', {})
            books.append({
                'title': volume.get('title', 'Untitled'),
                'author': ', '.join(volume.get('authors', [])),
                'description': volume.get('description', '')[:200],  # limit to 200 chars
                'thumbnail': volume.get('imageLinks', {}).get('thumbnail', ''),
            })

        # Return books as JSON response
        return JsonResponse({'books': books})
    
    except Exception as e:
        # Return error if request or parsing fails
        return JsonResponse({'error': str(e)}, status=500)

