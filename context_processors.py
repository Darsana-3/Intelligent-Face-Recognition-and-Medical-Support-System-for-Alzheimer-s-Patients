from .helpers import get_logged_user
from .models import Notification


def notifications_processor(request):
    """Inject unread notifications count into all templates."""
    role, user = get_logged_user(request)
    unread = 0
    notifications = []
    if role and user:
        qs = Notification.objects.filter(recipient_role=role, recipient_id=user.id, is_read=False)
        unread = qs.count()
        notifications = list(qs[:5])
    return {
        'logged_role': role,
        'logged_user': user,
        'unread_notifications_count': unread,
        'recent_notifications': notifications,
    }
