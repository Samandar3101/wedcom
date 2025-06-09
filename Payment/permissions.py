from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a payment or admins to access it.
    """
    def has_object_permission(self, request, _, obj):
        # Admin users have full access
        if getattr(request.user, 'is_admin', False):
            return True
            
        # Payment owners can access their own payments
        return obj.user == request.user

class IsCourseInstructorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow course instructors or admins to access course payments.
    """
    def has_object_permission(self, request, _, obj):
        # Admin users have full access
        if getattr(request.user, 'is_admin', False):
            return True
            
        # Course instructors can access their course payments
        return hasattr(obj.course, 'instructor') and obj.course.instructor == request.user

class IsPaymentProvider(permissions.BasePermission):
    """
    Custom permission to only allow payment providers to access webhook endpoints.
    """
    def has_permission(self, request, _):
        # Check for provider signature in headers
        return bool(request.headers.get('X-Signature')) 