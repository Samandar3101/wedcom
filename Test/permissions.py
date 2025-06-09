from rest_framework import permissions

class IsTestOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of a test or admins to access it.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.role == 'admin':
            return True
            
        # Test owners can access their own tests
        return obj.created_by == request.user

class IsTestTaker(permissions.BasePermission):
    """
    Custom permission to only allow students who are enrolled in the course to take tests.
    """
    def has_object_permission(self, request, view, obj):
        # Admin users have full access
        if request.user.role == 'admin':
            return True
            
        # Course instructors can access their course tests
        if request.user.role == 'teacher' and obj.course.instructor == request.user:
            return True
            
        # Students can access tests for courses they are enrolled in
        return request.user.role == 'student' and obj.course.students.filter(id=request.user.id).exists()

class IsAdminOrTeacher(permissions.BasePermission):
    """
    Custom permission to only allow admin users or teachers to access certain endpoints.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['admin', 'teacher']

class IsStudent(permissions.BasePermission):
    """
    Custom permission to only allow students to access certain endpoints.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsCourseInstructorOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow course instructors or admins to modify objects.
    """

    def has_permission(self, request, view):
        # Allow read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions are only allowed to course instructors or admins
        return request.user and request.user.is_authenticated and (
            request.user.role == 'teacher' or request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated

        # Write permissions are only allowed to the course instructor or admins
        if hasattr(obj, 'course'):
            return request.user and request.user.is_authenticated and (
                obj.course.instructor == request.user or request.user.is_admin
            )
        elif hasattr(obj, 'test'):
            return request.user and request.user.is_authenticated and (
                obj.test.course.instructor == request.user or request.user.is_admin
            )
        return False 