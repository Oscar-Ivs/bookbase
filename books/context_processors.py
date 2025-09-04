from .models import CommentNotification


def unread_comments_count(request):
    """
    Makes the number of unread comment notifications available globally (e.g. in navbar).
    """
    if request.user.is_authenticated:
        return {
            "unread_comments_count": CommentNotification.objects.filter(
                user=request.user, is_read=False
            ).count()
        }
    return {"unread_comments_count": 0}
