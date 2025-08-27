# books/views.py
"""
BookBase Views

This module contains all views for BookBase:
- Authentication (register, logout)
- Core pages (home, about, profile, my_collection)
- Book CRUD (add/edit/delete)
- Google Books integrations (search for Add Book + homepage discovery grid)
- Unified Book Detail (DB + Google ID) with comments + pagination
- Comment management and notifications
- Community directory + public profiles (login required to view a profile)

UX Intent:
- Guests can browse homepage and open book details (including Google items).
- Guests can see Community directory, but must login to open a specific profile.
- Authenticated users manage their collection and can comment on DB books.
"""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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
    """Register a new user and redirect home."""
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
    """Log out the current user via GET and redirect home."""
    logout(request)
    return redirect('home')


# ============================================================================
# Core Pages
# ============================================================================

def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


@login_required
def profile(request):
    """
    Profile page:
    - Bio edit (inline)
    - Avatar upload (resized ~300x300)
    - Public/private toggle (separate POST)
    - Username/email update (separate POST)
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
                obj.is_public = profile.is_public  # preserve visibility
                obj.save()

                # Optional: resize uploaded avatar
                if 'avatar' in request.FILES and obj.avatar:
                    try:
                        avatar_path = obj.avatar.path
                        img = Image.open(avatar_path).convert('RGB')
                        img.thumbnail((300, 300))
                        img.save(avatar_path, format='JPEG', quality=85)
                    except Exception as exc:
                        print("Image resize error:", exc)

                return redirect('profile')

        # (2) Visibility toggle
        elif 'toggle_visibility' in request.POST:
            profile.is_public = (request.POST.get('is_public') == 'on')
            profile.save(update_fields=['is_public'])
            return redirect('profile')

        # (3) Username/email update
        elif 'update_user_form' in request.POST:
            if user_form.is_valid():
                user_form.save()
                return redirect('profile')

    # Stats for display
    qs = Book.objects.filter(user=request.user)
    context = {
        'profile': profile,
        'form': profile_form,
        'user_form': user_form,
        'read_count': qs.filter(status='read').count(),
        'unread_count': qs.filter(status='unread').count(),
        'total_books': qs.count(),
        'bio_background': '#acbdd8',
    }
    return render(request, 'profile.html', context)


@login_required
def my_collection(request):
    """
    Show the current user's books with:
    - Sort controls via ?sort=
    - Grid/List toggle via ?view=
    - Unread comment badges per book
    """
    # ---- Sorting
    sort = request.GET.get('sort', 'title_asc')
    order_map = {
        'title_asc': ['title', 'author'],
        'title_desc': ['-title', 'author'],
        'author_asc': ['author', 'title'],
        'author_desc': ['-author', 'title'],
        'recent': ['-id'],  # proxy for "recently added" without migrations
        'status_read_first': ['status', 'title'],    # 'read' < 'unread'
        'status_unread_first': ['-status', 'title'],
    }
    order_by = order_map.get(sort, ['title', 'author'])

    # ---- View mode
    view_mode = request.GET.get('view', 'grid')  # 'grid' or 'list'

    books = Book.objects.filter(user=request.user).order_by(*order_by)

    # Unread notifications per book
    unread_qs = (
        CommentNotification.objects
        .filter(user=request.user, is_read=False, comment__book__user=request.user)
        .values('comment__book_id')
        .annotate(count=Count('id'))
    )
    unread_by_book = {row['comment__book_id']: row['count'] for row in unread_qs}
    for b in books:
        b.unread_count = unread_by_book.get(b.id, 0)

    return render(
        request,
        'my_collection.html',
        {
            'books': books,
            'sort': sort,
            'view_mode': view_mode,
        },
    )


# ============================================================================
# Book CRUD
# ============================================================================

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


@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    if request.method == 'POST':
        book.delete()
        return redirect('my_collection')
    return render(request, 'delete_book.html', {'book': book})


# ============================================================================
# Google Books AJAX
# ============================================================================

def search_google_books(request):
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
# Unified Book Detail (DB + Google) + Comments with Pagination
# ============================================================================

def book_detail(request, book_id):
    """
    Guests can view book details (DB or Google).
    Authenticated users can post comments on DB books.
    Comments are paginated (10 per page) and long comments can expand in the UI.
    """
    db_book = None
    try:
        # Try DB book (integer id)
        int_id = int(book_id)
        db_book = (
            Book.objects.filter(id=int_id, user=request.user).first()
            or Book.objects.filter(id=int_id, user__profile__is_public=True).first()
        )
        if not db_book:
            raise Book.DoesNotExist

        # Owner opens their book → mark notifs read
        if request.user.is_authenticated and db_book.user == request.user:
            CommentNotification.objects.filter(
                user=request.user, comment__book=db_book, is_read=False
            ).update(is_read=True)

        # POST comment (auth only)
        if request.method == 'POST':
            if not request.user.is_authenticated:
                login_url = f"{reverse('login')}?next={request.get_full_path()}"
                return redirect(login_url)

            text = (request.POST.get('comment_text') or '').strip()
            if text:
                comment = Comment.objects.create(book=db_book, user=request.user, text=text)
                if db_book.user != request.user:
                    CommentNotification.objects.create(
                        user=db_book.user,
                        comment=Comment.objects.filter(book=db_book, user=request.user).latest("created_at"),
                        is_read=False,
                    )
                messages.success(request, "Comment added.")
            return redirect('book_detail', book_id=db_book.id)

        # GET: comments (paginated)
        comments_qs = (
            Comment.objects
            .filter(book=db_book)
            .select_related('user')
            .order_by('-created_at')
        )
        paginator = Paginator(comments_qs, 10)
        page = request.GET.get('page', 1)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

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
        return render(
            request,
            'book_detail.html',
            {'book': book_data, 'page_obj': page_obj, 'paginator': paginator}
        )

    except (ValueError, ValidationError, Book.DoesNotExist):
        pass

    # Fallback: Google Books (API)
    api_url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    response = requests.get(api_url)
    if response.status_code != 200:
        return render(
            request, 'book_detail.html',
            {'book': {'title': 'Book not found', 'description': 'Unable to fetch data.',
                      'cover_url': '/static/img/book-placeholder.png'}}
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
    return render(request, 'book_detail.html', {'book': book_data, 'page_obj': None})


# ============================================================================
# Comment Management & Notifications
# ============================================================================

@login_required
def delete_comment(request, comment_id):
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
    Mark all unread notifications for current user.
    NOTE: If your model field is `user`, update the filter accordingly.
    """
    if request.method == 'POST':
        # Keep as-is if you're intentionally using 'recipient' elsewhere.
        CommentNotification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)  # noqa: E501
        messages.success(request, "All notifications marked as read.")
    return redirect('my_collection')


# ============================================================================
# Community
# ============================================================================

def community_list(request):
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
    profile = get_object_or_404(Profile, user__username=username, is_public=True)
    books = Book.objects.filter(user=profile.user).order_by('title')
    return render(request, 'community_profile.html', {'profile': profile, 'books': books})
