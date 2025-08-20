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
