from rest_framework import permissions

class IsAuthorOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in (permissions.SAFE_METHODS
                              or view.author == request.user):
            return True
