# permissions.py
from functools import wraps
from django.http import HttpResponseForbidden

def role_required(*roles):
    """
    Decorator to check if user has the required role.
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("Authentication required")
            if not request.user.has_role(*roles):
                return HttpResponseForbidden("You don't have permission to access this page")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

def admin_required(view_func):
    """
    Decorator to check if user is admin.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Authentication required")
        if not request.user.is_admin():
            return HttpResponseForbidden("Admin access required")
        return view_func(request, *args, **kwargs)
    return _wrapped_view