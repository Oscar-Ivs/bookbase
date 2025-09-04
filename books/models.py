# books/models.py
"""
BookBase Models

Entities:
- Book: A single book entry owned by a user (CRUD + notes + status).
- Profile: Extended user profile (avatar, bio, public visibility).
- Comment: User comment left on a DB book.
- CommentNotification: Unread/read notification for book owners when comments arrive.

Notes:
- We keep Google Books data (thumbnail, description) via simple URL/text fields.
- 'is_public' lives on Profile so users can opt in to sharing.
- CommentNotification links to Comment (and indirectly to Book via comment.book).
"""

from django.contrib.auth.models import User
from django.db import models


class Book(models.Model):
    """A single book in a user's personal collection."""

    STATUS_CHOICES = [
        ("read", "Read"),
        ("unread", "Not Read"),
    ]

    title = models.CharField(
        max_length=200,
        help_text="Book title (from Google Books or manual entry).",
    )
    author = models.CharField(
        max_length=200,
        help_text="Primary author(s). Use comma-separated values if multiple.",
    )
    description = models.TextField(
        blank=True,
        help_text="Optional summary/description.",
    )
    cover_url = models.URLField(
        max_length=500,
        blank=True,
        help_text="Thumbnail URL (e.g., Google Books image link).",
    )
    google_book_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="If sourced from Google Books, the volume ID goes here.",
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="unread",
        help_text="Track whether you've read this book.",
    )
    notes = models.TextField(
        blank=True,
        help_text="Private notes for this book.",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="Owner of this book entry.",
    )

    class Meta:
        ordering = ["title", "author"]  # Consistent, user-friendly listing
        verbose_name = "Book"
        verbose_name_plural = "Books"

    def __str__(self):
        return f"{self.title} by {self.author}"


class Profile(models.Model):
    """Extended user profile: avatar, short bio, and public visibility flag."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        help_text="The Django auth user this profile belongs to.",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text="Optional profile image. Resized on upload for performance.",
    )
    bio = models.TextField(
        blank=True,
        null=True,
        help_text="Optional short bio shown on your profile.",
    )
    is_public = models.BooleanField(
        default=False,
        help_text="If true, signed-in users can view your profile & collection.",
    )

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.user.username}'s profile"


class Comment(models.Model):
    """
    A comment left on a DB-backed book.
    Auth rules (handled in views/templates):
      - Only authenticated users can create comments.
      - Comment author OR book owner can delete.
    """

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name="comments",
        help_text="The book this comment refers to.",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The user who wrote this comment.",
    )
    text = models.TextField(
        help_text="The comment body.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the comment was created.",
    )
    # Optional convenience flag; real unread state for owners is tracked via CommentNotification
    is_read = models.BooleanField(
        default=False,
        help_text="Local read flag (not used for badges; notifications handle that).",
    )

    class Meta:
        ordering = ["-created_at"]  # Latest comments first
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user.username} on {self.book.title}"


class CommentNotification(models.Model):
    """
    Notification for a book owner when a new comment is posted.
    The 'user' field here refers to the recipient (book owner), not the author
    of the comment. We keep a simple read/unread boolean for the UI badge.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="Notification recipient (book owner).",
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        help_text="The comment that triggered this notification.",
    )
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the recipient has read this notification.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this notification was created.",
    )

    class Meta:
        ordering = ["-created_at"]  # Show newest notifications first
        verbose_name = "Comment notification"
        verbose_name_plural = "Comment notifications"

    def __str__(self):
        return f"Notification for {self.user.username} - {self.comment.text[:20]}"
