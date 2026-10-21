"""Helper functions used across apps."""
import re
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from .models import Admin, Doctor, Patient, Notification, ActivityLog


# -------- VALIDATION HELPERS --------
PHONE_REGEX = re.compile(r'^[0-9]{10}$')
PASSWORD_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$')
ALLOWED_EMAIL_DOMAINS = {
    'gmail.com', 'googlemail.com', 'google.com',
    'yahoo.com', 'yahoo.co.in', 'ymail.com',
    'outlook.com', 'hotmail.com', 'live.com', 'msn.com',
}


def validate_phone(phone):
    """Return True if phone is exactly 10 digits."""
    return bool(PHONE_REGEX.match((phone or '').strip()))


def validate_password_strength(password):
    """Return True if password has 8+ chars with upper, lower, digit and special char."""
    return bool(PASSWORD_REGEX.match(password or ''))


def validate_email_domain(email):
    """Return True if the email's domain is a well-known provider (gmail, yahoo, outlook, etc.)."""
    email = (email or '').strip().lower()
    if '@' not in email:
        return False
    domain = email.rsplit('@', 1)[-1]
    return domain in ALLOWED_EMAIL_DOMAINS


def get_logged_user(request):
    """Return (role, user_obj) tuple if logged in, else (None, None)."""
    role = request.session.get('role')
    uid = request.session.get('user_id')
    if not role or not uid:
        return None, None
    try:
        if role == 'admin':
            return 'admin', Admin.objects.get(id=uid)
        if role == 'doctor':
            return 'doctor', Doctor.objects.get(id=uid)
        if role == 'patient':
            return 'patient', Patient.objects.get(id=uid)
    except (Admin.DoesNotExist, Doctor.DoesNotExist, Patient.DoesNotExist):
        return None, None
    return None, None


def login_required_role(allowed_roles):
    """Decorator restricting view to specific role(s)."""
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapper(request, *args, **kwargs):
            role, user = get_logged_user(request)
            if not role or role not in allowed_roles:
                messages.error(request, "Please login to continue.")
                return redirect('login')
            request.role = role
            request.user_obj = user
            return view_func(request, *args, **kwargs)
        return _wrapper
    return decorator


def create_notification(role, uid, title, message, notif_type='general'):
    Notification.objects.create(
        recipient_role=role,
        recipient_id=uid,
        title=title,
        message=message,
        notif_type=notif_type,
    )


def log_activity(role, uid, name, action, request=None):
    ip = None
    if request:
        x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
        ip = x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')
    ActivityLog.objects.create(
        user_role=role,
        user_id=uid,
        user_name=name,
        action=action,
        ip_address=ip,
    )


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')
