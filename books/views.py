# books/views.py
"""
BookBase Views

This module contains all views for BookBase:
- Authentication (register, logout)
- Core pages (home, about, profile, my_collection)
- Book CRUD (add/edit/delete)
- Google Books integrations (search for Add Book + homepage discovery grid)
- Unified Book Detail (works for both DB books and Google Books IDs)
- Comment management and notifications
- Community directory + public profiles (login required to view a profile)

Design Intent (UX):
- Guests:
  * Can browse the homepage and open book details (including Google Books items).
  * Can see the Community directory list but cannot open individual user profiles.
- Authenticated users:
  * Can manage their own collection (CRUD).
  * Can open other users’ public profiles and comment on DB books.
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

import requests
from PIL import Image  # used to resize avatars

from .forms import BookForm, ProfileForm, UserUpdateForm
from .models import Book, Comment, CommentNotification, Profile


# ============================================================================
# Authentication
# ============================================================================

def register(request):
    """
    Simple user registration using Django's built-in UserCreationForm.
    On success, logs the user in and redirects to home.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def logout_view(request):
    """
    Log out the current user via GET and redirect to the homepage.
    Django's default LogoutView expects POST; this custom view keeps your GET flow.
    """
    logout(request)
    return redirect('home')


# ============================================================================
# Core Pages
# ============================================================================

def home(request):
    """Landing page with Google Books discovery grid (loaded via AJAX)."""
    return render(request, 'home.html')


def about(request):
    """Simple About page."""
    return render(request, 'about.html')


@login_required
def profile(request):
    """
    Profile page:
    - Bio edit (inline)
    - Avatar upload (auto-resized to ~300x300, compressed)
    - Public/private toggle (separate POST branch)
    - Username/email update (separate POST branch)
    Implementation keeps 'is_public' changes isolated so bio/avatar edits don't affect it.
    """
    profile, _ = Profile.objects.get_or_create(user=request.user)

    profile_form = ProfileForm(
        request.POST or None,
        request.FILES or None,
        instance=profile,
    )
    user_form = UserUpdateForm(request.POST or None, instance=request.user)

    if request.method == 'POST':
        # (1) Bio and/or Avatar change
        if 'update_bio' in request.POST or 'avatar' in request.FILES:
            if profile_form.is_valid():
                obj = profile_form.save(commit=False)
                # Preserve visibility flag (do not toggle from this form)
                obj.is_public = profile.is_public
                obj.save()

                # Optional: resize uploaded avatar safely
                if 'avatar' in request.FILES and obj.avatar:
                    try:
                        avatar_path = obj.avatar.path
                        img = Image.open(avatar_path).convert('RGB')
                        img.thumbnail((300, 300))
                        img.save(avatar_path, format='JPEG', quality=85)
                    except Exception as exc:
                        # Non-fatal: do not block the request
                        print("Image resize error:", exc)

                return redirect('profile')

        # (2) Visibility toggle (separate form/branch)
        elif 'toggle_visibility' in request.POST:
            profile.is_public = (request.POST.get('is_public') == 'on')
            profile.save(update_fields=['is_public'])
            return redirect('profile')

        # (3) Username / email update
        elif 'update_user_form' in request.POST:
            if user_form.is_valid():
                user_form.save()
                return redirect('profile')

    # Stats for display blocks
    qs = Book.objects.filter(user=request.user)
    context = {
        'profile': profile,
        'form': profile_form,
        'user_form': user_form,
        'read_count': qs.filter(status='read').count(),
        'unread_count': qs.filter(status='unread').count(),
        'total_books': qs.count(),
        # Inline style helper for the card background to keep theme consistent
        'bio_background': '#acbdd8',
    }
    return render(request, 'profile.html', context)


@login_required
def my_collection(request):
    """
    Show the current user's books with per-book unread notification counts.
    Unread counts are computed via CommentNotification linked through Comment→Book.
    """
    books = Book.objects.filter(user=request.user).order_by('title')

    # Map unread notifications per book for quick display badges.
    unread_qs = (
        CommentNotification.objects
        .filter(user=request.user, is_read=False, comment__book__user=request.user)
        .values('comment__book_id')
        .annotate(count=Count('id'))
    )
    unread_by_book = {row['comment__book_id']: row['count'] for row in unread_qs}

    for b in books:
        b.unread_count = unread_by_book.get(b.id, 0)

    return render(request, 'my_collection.html', {'books': books})


# ============================================================================
# Book CRUD
# ============================================================================

@login_required
def add_book(request):
    """
    Create a new Book owned by the current user.
    The Add form can be prefilled via Google Books search (AJAX on the same page).
    """
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


@login_required
def edit_book(request, book_id):
    """Edit an existing book (owner only)."""
    book = get_object_or_404(Book, id=book_id, user=request.user)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect('my_collection')
    else:
        form = BookForm(instance=book)
    return render(request, 'edit_book.html', {'form': form, 'book': book})


@login_required
def delete_book(request, book_id):
    """Delete a book (owner only) with a standard POST confirmation."""
    book = get_object_or_404(Book, id=book_id, user=request.user)
    if request.method == 'POST':
        book.delete()
        return redirect('my_collection')
    return render(request, 'delete_book.html', {'book': book})


# ============================================================================
# Google Books AJAX Endpoints
# ============================================================================

def search_google_books(request):
    """
    AJAX endpoint used on Add Book page.
    Given a query + paging options, returns a small list of Google Books to allow autofill.
    Response key is 'books' (expected by the frontend).
    """
    query = request.GET.get('q', '')
    start_index = int(request.GET.get('startIndex', 0))
    max_results = int(request.GET.get('maxResults', 6))

    if not query:
        return JsonResponse({'error': 'No query provided'}, status=400)

    url = (
        'https://www.googleapis.com/books/v1/volumes'
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
                'description': info.get('description', ''),
                'cover_url': info.get('imageLinks', {}).get('thumbnail', ''),
                'id': item.get('id'),
            })

        return JsonResponse({'books': books})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


def fetch_books(request):
    """
    AJAX endpoint used by the homepage discovery grid.
    Supports search + sort + paging. Always returns at most 24 items per batch.
    """
    query = request.GET.get('q', 'fiction')
    order = request.GET.get('order', 'relevance')
    start_index = int(request.GET.get('startIndex', 0))
    max_results = 24

    url = (
        'https://www.googleapis.com/books/v1/volumes'
        f'?q={query}&orderBy={order}&startIndex={start_index}&maxResults={max_results}'
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
                'description': (volume.get('description', '')[:300]),
                'cover_url': volume.get('imageLinks', {}).get('thumbnail', ''),
                'id': item.get('id'),
            })

        return JsonResponse({'books': books})
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


# ============================================================================
# Unified Book Detail (DB + Google) + Comments
# ============================================================================

def book_detail(request, book_id):
    """
    Unified detail view:

    - If book_id is an integer and we can find a matching DB book owned by the
      current user OR belonging to any public profile → render DB details and comments.
    - Otherwise we treat book_id as a Google Books ID and fetch details from the API.

    Access model (your chosen UX):
    - Guests CAN view book details (DB or Google).
    - Posting comments requires login. If a guest tries to POST, redirect to /login/?next=...
    """
    db_book = None
    try:
        # Attempt DB path (int id)
        int_id = int(book_id)

        # First try owner; then any public user's book
        db_book = (
            Book.objects.filter(id=int_id, user=request.user).first()
            or Book.objects.filter(id=int_id, user__profile__is_public=True).first()
        )
        if not db_book:
            raise Book.DoesNotExist

        # Mark notifications as read when the owner views their own book
        if request.user.is_authenticated and db_book.user == request.user:
            CommentNotification.objects.filter(
                user=request.user,
                comment__book=db_book,
                is_read=False
            ).update(is_read=True)

        # POST => add a comment (authentication required)
        if request.method == 'POST':
            if not request.user.is_authenticated:
                # Respect your configured login route and preserve redirection target
                login_url = f"{reverse('login')}?next={request.get_full_path()}"
                return redirect(login_url)

            text = (request.POST.get('comment_text') or '').strip()
            if text:
                comment = Comment.objects.create(
                    book=db_book,
                    user=request.user,
                    text=text
                )
                if db_book.user != request.user:
                    # Create a notification for the book owner, referencing the new comment
                    CommentNotification.objects.create(
                        user=db_book.user,
                        comment=Comment.objects.filter(
                            book=db_book,
                            user=request.user
                        ).latest("created_at"),
                        is_read=False,
                    )
                messages.success(request, "Comment added.")

            return redirect('book_detail', book_id=db_book.id)

        # GET => render DB detail (with comments)
        comments = (
            Comment.objects
            .filter(book=db_book)
            .select_related('user')
            .order_by('-created_at')
        )

        is_owner = (request.user.is_authenticated and db_book.user == request.user)
        book_data = {
            'id': db_book.id,
            'title': db_book.title,
            'author': db_book.author,
            'description': db_book.description,
            'notes': getattr(db_book, 'notes', None),
            'cover_url': db_book.cover_url or '/static/img/book-placeholder.png',
            'status': db_book.status,
            'is_owner': is_owner,
        }
        return render(request, 'book_detail.html', {'book': book_data, 'comments': comments})

    except (ValueError, ValidationError, Book.DoesNotExist):
        # Not an int, or no DB book found → fall back to Google Books
        pass

    # --- Fallback: Google Books API flow (no comments on API-only books) ---
    api_url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    response = requests.get(api_url)

    if response.status_code != 200:
        # Render with a friendly message if the API cannot find the book
        return render(
            request,
            'book_detail.html',
            {
                'book': {
                    'title': 'Book not found',
                    'description': 'Unable to fetch data.',
                    'cover_url': '/static/img/book-placeholder.png',
                }
            }
        )

    data = response.json().get('volumeInfo', {})
    book_data = {
        'title': data.get('title', 'No title'),
        'author': ', '.join(data.get('authors', [])),
        'description': data.get('description', 'No description available.'),
        'cover_url': data.get('imageLinks', {}).get('thumbnail', '/static/img/book-placeholder.png'),
        'publisher': data.get('publisher', 'Unknown'),
        'publishedDate': data.get('publishedDate', 'N/A'),
        'pageCount': data.get('pageCount', 'N/A'),
    }
    return render(request, 'book_detail.html', {'book': book_data, 'comments': []})


# ============================================================================
# Comment Management & Notifications
# ============================================================================

@login_required
def delete_comment(request, comment_id):
    """
    Allow the comment author OR the book owner to delete a comment.
    Clean up related notifications before deleting the comment.
    """
    comment = get_object_or_404(Comment, id=comment_id)
    is_owner = (comment.book.user == request.user)
    is_author = (comment.user == request.user)

    if not (is_owner or is_author):
        return HttpResponseForbidden("You don't have permission to delete this comment.")

    if request.method == 'POST':
        CommentNotification.objects.filter(comment=comment).delete()
        comment.delete()
        messages.success(request, "Comment deleted.")
        return redirect('book_detail', book_id=comment.book.id)

    return redirect('book_detail', book_id=comment.book.id)


@login_required
def mark_all_notifications_read(request):
    """
    Mark all unread comment notifications for the current user as read.
    NOTE: If your CommentNotification model uses `user` (not `recipient`),
    the filter should be .filter(user=request.user, is_read=False).
    This function currently mirrors your existing code path; update when ready.
    """
    if request.method == 'POST':
        # If your model field is `user`, change `recipient` → `user` here.
        CommentNotification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)  # noqa: E501
        messages.success(request, "All notifications marked as read.")
    return redirect('my_collection')


# ============================================================================
# Community
# ============================================================================

def community_list(request):
    """
    Public directory of users who opted into sharing (is_public=True).
    Guests can see the list; 'View Profile' button is shown only to logged-in users.
    """
    profiles = Profile.objects.filter(is_public=True).select_related('user')
    public_users = []
    for p in profiles:
        qs = Book.objects.filter(user=p.user)
        public_users.append({
            'username': p.user.username,
            'avatar_url': (p.avatar.url if p.avatar else '/static/img/avatar-placeholder.png'),
            'bio': p.bio,
            'member_since': p.user.date_joined,
            'total_books': qs.count(),
            'read_count': qs.filter(status='read').count(),
            'unread_count': qs.filter(status='unread').count(),
        })
    return render(request, 'community_list.html', {'profiles': public_users})


@login_required
def community_profile(request, username):
    """
    Individual shared collection page (requires login per your UX decision).
    Only profiles with is_public=True are accessible.
    """
    profile = get_object_or_404(Profile, user__username=username, is_public=True)
    books = Book.objects.filter(user=profile.user).order_by('title')
    return render(request, 'community_profile.html', {'profile': profile, 'books': books})
