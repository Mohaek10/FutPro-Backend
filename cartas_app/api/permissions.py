from rest_framework import permissions


class IsAdminorReadOnly(permissions.IsAdminUser):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        staff_permissions = bool(request.user and request.user.is_admin)
        return staff_permissions


class IsComentarioUserOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return obj.comentario_user == request.user or request.user.is_admin
