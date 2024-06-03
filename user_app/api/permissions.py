from rest_framework import permissions


class IsAdminorReadOnly(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        staff_permissions = bool(request.user and request.user.is_staff)
        return staff_permissions
