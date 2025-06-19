from django.contrib.auth.backends import ModelBackend

class RoleBasedModelBackend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        # Superusers have all permissions
        if user_obj.is_superuser:
            return True
            
        # Check Django's default permissions
        has_perm = super().has_perm(user_obj, perm, obj)
        if has_perm:
            return True
            
        # Implement role-specific permissions
        if perm == 'app.view_sensitive_data' and user_obj.has_role('admin', 'vendor'):
            return True
            
        if perm == 'app.edit_content' and user_obj.has_role('admin', 'seller'):
            return True
            
        return False