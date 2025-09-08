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
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

import requests
from requests import exceptions as req_exc
from PIL import Image  # used to resize avatars
import logging

from .forms import BookForm, ProfileForm, UserUpdateForm
from .models import Book, Comment, CommentNotification, Profile


# --- helpers ---------------------------------------------------------------
def _https_thumb(url: str) -> str:
    """Force Google Books thumbnails to https to avoid mixed-content."""
    return url.replace("http://", "https://") if isinstance(url, str) else ""


def _author_str(authors) -> str:
    """Join authors safely; return a friendly fallback."""
    if not authors:
        return "Unknown Author"
    try:
        return ", ".join([a.strip() for a in authors if a and isinstance(a, str)])
    except Exception:
        return "Unknown Author"


# ============================================================================  
# Authentication  
# ============================================================================  

def register(request):
    """Register a new user and redirect home."""
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    """Log out the current user via GET and redirect home."""
    logout(request)
    return redirect("home")


# ============================================================================  
# Core Pages  
# ============================================================================  

def home(request):
    return render(request, "home.html")


def about(request):
    return render(request, "about.html")


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

    if request.method == "POST":
        # (1) Bio and/or Avatar change
        if "update_bio" in request.POST or "avatar" in request.FILES:
            if profile_form.is_valid():
                obj = profile_form.save(commit=False)
                obj.is_public = profile.is_public  # preserve visibility
                obj.save()

                # Optional: resize uploaded avatar (only if local FileSystemStorage)
                if "avatar" in request.FILES and obj.avatar:
                    try:
                        avatar_path = obj.avatar.path
                        img = Image.open(avatar_path)
                        if img.mode not in ("RGB", "L"):
                            img = img.convert("RGB")
                        img.thumbnail((300, 300))
                        img.save(avatar_path, format="JPEG", quality=85, optimize=True)
                    except Exception as exc:
                        logging.getLogger(__name__).exception(
                            "Avatar processing failed: %s", exc
                        )
                return redirect("profile")

        # (2) Visibility toggle
        elif "toggle_visibility" in request.POST:
            profile.is_public = request.POST.get("is_public") == "on"
            profile.save(update_fields=["is_public"])
            return redirect("profile")

        # (3) Username/email update
        elif "update_user_form" in request.POST:
            if user_form.is_valid():
                user_form.save()
                return redirect("profile")

    # Stats for display
    qs = Book.objects.filter(user=request.user)
    context = {
        "profile": profile,
        "form": profile_form,
        "user_form": user_form,
        "read_count": qs.filter(status="read").count(),
        "unread_count": qs.filter(status="unread").count(),
        "total_books": qs.count(),
        "bio_background": "#acbdd8",
    }
    return render(request, "profile.html", context)

@login_required
def my_collection(request):
    """
    Show the current user's books with:
    - Sort controls via ?sort=
    - Grid/List toggle via ?view=
    - Persist view per-account using session (keyed by username)
    - Unread comment badges per book
    """
    # ---- Sorting
    sort = request.GET.get("sort", "title_asc")
    order_map = {
        "title_asc": ["title", "author"],
        "title_desc": ["-title", "author"],
        "author_asc": ["author", "title"],
        "author_desc": ["-author", "title"],
        "recent": ["-id"],
        "status_read_first": ["status", "title"],  # 'read' < 'unread'
        "status_unread_first": ["-status", "title"],
    }
    order_by = order_map.get(sort, ["title", "author"])

    # ---- Per-user view preference via session
    sess_key = f"collectionView:{request.user.username}"
    view_from_query = request.GET.get("view")
    if view_from_query in ("grid", "list"):
        request.session[sess_key] = view_from_query  # save per user
        view_mode = view_from_query
    else:
        view_mode = request.session.get(sess_key, "grid")

    # ---- Query books
    books = Book.objects.filter(user=request.user).order_by(*order_by)

    # Unread notifications per book
    unread_qs = (
        CommentNotification.objects.filter(
            user=request.user, is_read=False, comment__book__user=request.user
        )
        .values("comment__book_id")
        .annotate(count=Count("id"))
    )
    unread_by_book = {row["comment__book_id"]: row["count"] for row in unread_qs}
    for b in books:
        b.unread_count = unread_by_book.get(b.id, 0)

    return render(
        request,
        "my_collection.html",
        {
            "books": books,
            "sort": sort,
            "view_mode": view_mode,
        },
    )


# ============================================================================
# Book CRUD
# ============================================================================


@login_required
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            new_book = form.save(commit=False)
            new_book.user = request.user
            new_book.save()
            return redirect("my_collection")
    else:
        form = BookForm()
    return render(request, "add_book.html", {"form": form})


@login_required
def edit_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect("my_collection")
    else:
        form = BookForm(instance=book)
    return render(request, "edit_book.html", {"form": form, "book": book})


@login_required
def delete_book(request, book_id):
    book = get_object_or_404(Book, id=book_id, user=request.user)
    if request.method == "POST":
        book.delete()
        return redirect("my_collection")
    return render(request, "delete_book.html", {"book": book})


# ============================================================================
# Google Books AJAX
# ============================================================================


def search_google_books(request):
    """
    Used by the Add Book screen's inline search/autofill.
    """
    query = request.GET.get("q", "")
    start_index = int(request.GET.get("startIndex", 0))
    max_results = int(request.GET.get("maxResults", 6))

    if not query:
        return JsonResponse({"error": "No query provided"}, status=400)

    url = (
        "https://www.googleapis.com/books/v1/volumes"
        f"?q={query}&startIndex={start_index}&maxResults={max_results}&projection=full"
    )

    try:
        response = requests.get(url, timeout=8)
        data = response.json()
        books = []

        for item in data.get("items", []):
            info = item.get("volumeInfo", {}) or {}
            image_links = info.get("imageLinks", {}) or {}
            thumb = _https_thumb(image_links.get("thumbnail", ""))

            authors = info.get("authors") or []
            author_str = _author_str(authors)

            books.append(
                {
                    "id": item.get("id"),
                    "title": info.get("title", "Untitled"),
                    "author": author_str,
                    "description": info.get("description", ""),
                    "cover_url": thumb,
                    "thumbnail": thumb,
                }
            )

        return JsonResponse({"books": books})
    except (req_exc.RequestException, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=500)


def fetch_books(request):
    """
    Homepage discovery grid endpoint (/get_books/).
    Accepts: q, order (relevance|newest), startIndex, maxResults.
    """
    query = request.GET.get("q", "fiction")
    order = request.GET.get("order", "relevance")
    start_index = int(request.GET.get("startIndex", 0))
    max_results = int(request.GET.get("maxResults", 12))  # default 12 for better LCP

    url = (
        "https://www.googleapis.com/books/v1/volumes"
        f"?q={query}&orderBy={order}&startIndex={start_index}&maxResults={max_results}"
    )

    try:
        response = requests.get(url, timeout=8)
        data = response.json()
        books = []

        for item in data.get("items", []):
            volume = item.get("volumeInfo", {}) or {}
            image_links = volume.get("imageLinks", {}) or {}
            thumb = _https_thumb(image_links.get("thumbnail", ""))

            authors = volume.get("authors") or []
            author_str = _author_str(authors)

            books.append(
                {
                    "id": item.get("id"),
                    "title": volume.get("title", "Untitled"),
                    "author": author_str,
                    "description": (volume.get("description", "")[:300]),
                    "cover_url": thumb,
                    "thumbnail": thumb,
                }
            )

        return JsonResponse({"books": books})
    except (req_exc.RequestException, ValueError) as exc:
        return JsonResponse({"error": str(exc)}, status=500)


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
        if request.method == "POST":
            if not request.user.is_authenticated:
                login_url = f"{reverse('login')}?next={request.get_full_path()}"
                return redirect(login_url)

            text = (request.POST.get("comment_text") or "").strip()
            if text:
                comment = Comment.objects.create(
                    book=db_book, user=request.user, text=text
                )
                if db_book.user != request.user:
                    CommentNotification.objects.create(
                        user=db_book.user,
                        comment=comment,  # use the same comment we just created
                        is_read=False,
                    )
                messages.success(request, "Comment added.")
            return redirect("book_detail", book_id=db_book.id)

        # GET: comments (paginated)
        comments_qs = (
            Comment.objects.filter(book=db_book)
            .select_related("user")
            .order_by("-created_at")
        )
        paginator = Paginator(comments_qs, 10)
        page = request.GET.get("page", 1)
        try:
            page_obj = paginator.page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        is_owner = request.user.is_authenticated and db_book.user == request.user
        book_data = {
            "id": db_book.id,
            "title": db_book.title,
            "author": db_book.author,
            "description": db_book.description,
            "notes": getattr(db_book, "notes", None),
            "cover_url": db_book.cover_url or "/static/img/book-placeholder.png",
            "status": db_book.status,
            "is_owner": is_owner,
        }
        return render(
            request,
            "book_detail.html",
            {"book": book_data, "page_obj": page_obj, "paginator": paginator},
        )

    except (ValueError, ValidationError, Book.DoesNotExist):
        pass

    # Fallback: Google Books (API)
    api_url = f"https://www.googleapis.com/books/v1/volumes/{book_id}"
    try:
        response = requests.get(api_url, timeout=8)
        if response.status_code != 200:
            raise req_exc.RequestException(f"Bad status {response.status_code}")
        info = response.json().get("volumeInfo", {}) or {}
    except (req_exc.RequestException, ValueError):
        return render(
            request,
            "book_detail.html",
            {
                "book": {
                    "title": "Book not found",
                    "description": "Unable to fetch data.",
                    "cover_url": "/static/img/book-placeholder.png",
                }
            },
        )

    img_links = info.get("imageLinks", {}) or {}
    thumb = (
        _https_thumb(img_links.get("thumbnail", ""))
        or "/static/img/book-placeholder.png"
    )

    book_data = {
        "title": info.get("title", "No title"),
        "author": _author_str(info.get("authors")),
        "description": info.get("description", "No description available."),
        "cover_url": thumb,
        "publisher": info.get("publisher", "Unknown"),
        "publishedDate": info.get("publishedDate", "N/A"),
        "pageCount": info.get("pageCount", "N/A"),
    }
    return render(request, "book_detail.html", {"book": book_data, "page_obj": None})


# ============================================================================
# Comment Management & Notifications
# ============================================================================


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    is_owner = comment.book.user == request.user
    is_author = comment.user == request.user

    if not (is_owner or is_author):
        return HttpResponseForbidden(
            "You don't have permission to delete this comment."
        )

    if request.method == "POST":
        CommentNotification.objects.filter(comment=comment).delete()
        comment.delete()
        messages.success(request, "Comment deleted.")
        return redirect("book_detail", book_id=comment.book.id)

    return redirect("book_detail", book_id=comment.book.id)


@login_required
def mark_all_notifications_read(request):
    """Mark all unread notifications for current user."""
    if request.method == "POST":
        CommentNotification.objects.filter(user=request.user, is_read=False).update(
            is_read=True
        )
        messages.success(request, "All notifications marked as read.")
    return redirect("my_collection")


# ============================================================================
# Community
# ============================================================================


def community_list(request):
    """
    Public directory of users who chose to share their profile.
    - Sort options (username, most books, read/unread, recently joined)
    - Grid/List toggle, persisted per-account via session (guest isolated as 'guest')
    """
    # ---- sort
    sort = request.GET.get("sort", "username_asc")

    public_profiles = (
        Profile.objects.filter(is_public=True)
        .select_related("user")
        .annotate(
            total_books=Count("user__book", distinct=True),
            read_count=Count(
                "user__book", filter=Q(user__book__status="read"), distinct=True
            ),
            unread_count=Count(
                "user__book", filter=Q(user__book__status="unread"), distinct=True
            ),
        )
    )

    sort_map = {
        "username_asc": ["user__username"],
        "username_desc": ["-user__username"],
        "joined_recent": ["-user__date_joined"],
        "books_most": ["-total_books", "user__username"],
        "books_least": ["total_books", "user__username"],
        "read_most": ["-read_count", "user__username"],
        "unread_most": ["-unread_count", "user__username"],
    }
    public_profiles = public_profiles.order_by(*sort_map.get(sort, ["user__username"]))

    # ---- view mode persisted per account (or guest)
    who = request.user.username if request.user.is_authenticated else "guest"
    sess_key = f"communityView:{who}"
    view_from_query = request.GET.get("view")
    if view_from_query in ("grid", "list"):
        request.session[sess_key] = view_from_query
        view_mode = view_from_query
    else:
        view_mode = request.session.get(sess_key, "grid")

    context = {
        "profiles": public_profiles,
        "sort": sort,
        "view_mode": view_mode,
    }
    return render(request, "community_list.html", context)


@login_required
def community_profile(request, username):
    """
    Show a user's public profile + their books.
    - Requires login (guests can see community list but not profiles)
    - If the profile is private and it's not your own, redirect back with a message
    """
    target_user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=target_user)

    # Enforce visibility
    if not profile.is_public and target_user != request.user:
        messages.info(request, "This profile is private.")
        return redirect("community_list")

    # Books to display (all books owned by that user)
    sort = request.GET.get("sort", "title_asc")
    order_map = {
        "title_asc": ["title", "author"],
        "title_desc": ["-title", "author"],
        "author_asc": ["author", "title"],
        "author_desc": ["-author", "title"],
        "recent": ["-id"],
        "status_read_first": ["status", "title"],
        "status_unread_first": ["-status", "title"],
    }
    order_by = order_map.get(sort, ["title", "author"])

    books = Book.objects.filter(user=target_user).order_by(*order_by)

    return render(
        request,
        "community_profile.html",
        {
            "profile": profile,
            "books": books,
            "sort": sort,
        },
    )
