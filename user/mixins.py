# mixins.py
from django.core.exceptions import PermissionDenied

class RoleRequiredMixin:
    """
    Mixin to verify user has the required role.
    """
    required_roles = None
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required")
        
        if self.required_roles and not request.user.has_role(*self.required_roles):
            raise PermissionDenied("You don't have permission to access this page")
        
        return super().dispatch(request, *args, **kwargs)

class AdminRequiredMixin(RoleRequiredMixin):
    """
    Mixin to verify user is admin.
    """
    required_roles = ('admin',)
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise PermissionDenied("Authentication required")
        
        if not request.user.is_admin():
            raise PermissionDenied("Admin access required")
        
        return super().dispatch(request, *args, **kwargs)