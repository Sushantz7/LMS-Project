from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """Permission for Admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff

class IsInstructor(BasePermission):
    """Permission for Instructors."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "instructor"

class IsStudent(BasePermission):
    """Permission for Students."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "student"

class IsSponsor(BasePermission):
    """Permission for Sponsors."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == "sponsor"
