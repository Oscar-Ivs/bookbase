# books/admin.py
"""
BookBase Admin registrations

Provides convenient admin interfaces for:
- Book: owner, status, quick search on title/author/user, comments inline
- Profile: public/private flag, optional avatar, bio preview
- Comment: latest-first, search by book/user/text
- CommentNotification: mark as read/unread via actions

Notes:
- Uses inlines so you can see Comments on a Book.
- Adds admin actions for CommentNotification management.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Book, Profile, Comment, CommentNotification


# ---------------------------------------------------------------------------
# Inlines
# ---------------------------------------------------------------------------


class CommentInline(admin.TabularInline):
    """
    Show comments on the Book admin detail page.
    Compact view (TabularInline) and read-only created_at for clarity.
    """

    model = Comment
    extra = 0
    fields = ("user", "text", "created_at", "is_read")
    readonly_fields = ("created_at",)
    autocomplete_fields = ("user",)


# ---------------------------------------------------------------------------
# Book
# ---------------------------------------------------------------------------


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin for user-owned books.
    - search by title/author/owner username
    - filter by status
    - comments inline to quickly review activity
    """

    list_display = ("title", "author", "user", "status")
    list_filter = ("status", "user")
    search_fields = ("title", "author", "user__username")
    ordering = ("title", "author")
    autocomplete_fields = ("user",)
    inlines = [CommentInline]


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Admin for extended user profile.
    Shows a tiny avatar preview (if present) + visibility flag.
    """

    list_display = ("user", "is_public", "avatar_preview", "short_bio")
    list_filter = ("is_public",)
    search_fields = ("user__username", "user__email", "bio")
    autocomplete_fields = ("user",)

    def avatar_preview(self, obj):
        """Render a small avatar preview if available."""
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:40px;width:40px;object-fit:cover;border-radius:50%;">',
                obj.avatar.url,
            )
        return "—"

    avatar_preview.short_description = "Avatar"

    def short_bio(self, obj):
        """Truncate long bios for list display."""
        if not obj.bio:
            return "—"
        return (obj.bio[:60] + "…") if len(obj.bio) > 60 else obj.bio

    short_bio.short_description = "Bio"


# ---------------------------------------------------------------------------
# Comment
# ---------------------------------------------------------------------------


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin for comments on books.
    """

    list_display = ("book", "user", "short_text", "created_at", "is_read")
    list_filter = ("is_read", "created_at", "user")
    search_fields = ("book__title", "user__username", "text")
    ordering = ("-created_at",)
    autocomplete_fields = ("book", "user")
    readonly_fields = ("created_at",)

    def short_text(self, obj):
        """Shorten comment text for clearer list display."""
        return (obj.text[:60] + "…") if len(obj.text) > 60 else obj.text

    short_text.short_description = "Comment"


# ---------------------------------------------------------------------------
# Comment Notifications
# ---------------------------------------------------------------------------


@admin.action(description="Mark selected notifications as READ")
def mark_notifications_read(modeladmin, request, queryset):
    queryset.update(is_read=True)


@admin.action(description="Mark selected notifications as UNREAD")
def mark_notifications_unread(modeladmin, request, queryset):
    queryset.update(is_read=False)


@admin.register(CommentNotification)
class CommentNotificationAdmin(admin.ModelAdmin):
    """
    Admin for comment notifications.
    - Quick actions to flip read/unread state
    - Search by recipient username or comment text
    """

    list_display = ("user", "comment_snippet", "is_read", "created_at")
    list_filter = ("is_read", "created_at", "user")
    search_fields = ("user__username", "comment__text")
    ordering = ("-created_at",)
    autocomplete_fields = ("user", "comment")
    actions = [mark_notifications_read, mark_notifications_unread]
    readonly_fields = ("created_at",)

    def comment_snippet(self, obj):
        """Readable, shortened representation of the comment that triggered this notification."""
        text = obj.comment.text
        return (text[:60] + "…") if len(text) > 60 else text

    comment_snippet.short_description = "Comment"
