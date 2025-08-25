from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    STATUS_CHOICES = [
        ('read', 'Read'),
        ('unread', 'Not Read'),
    ]

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_url = models.URLField(max_length=500, blank=True)  # Image from Google Books
    google_book_id = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='unread')
    notes = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.title} by {self.author}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)   # bio stays optional
    is_public = models.BooleanField(
        default=False,
        help_text="Allow other signed-in users to view your profile and book collection."
    )

    def __str__(self):
        return f"{self.user.username}'s profile"


class Comment(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # track if owner has read

    def __str__(self):
        return f"Comment by {self.user.username} on {self.book.title}"


class CommentNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.comment.text[:20]}"
