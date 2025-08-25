from .models import Comment

def unread_comments_count(request):
    if not request.user.is_authenticated:
        return {'unread_comments_count': 0}
    count = Comment.objects.filter(book__user=request.user, is_read=False).count()
    return {'unread_comments_count': count}
