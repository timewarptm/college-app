from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsTeacher(BasePermission):
    """
    Allows access only to authenticated users who have the 'teacher' role.
    """
    message = "You must be a teacher to perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'

class IsStudent(BasePermission):
    """
    Allows access only to authenticated users who have the 'student' role.
    """
    message = "You must be a student to perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'student'

class IsCourseOwner(BasePermission):
    """
    Object-level permission to only allow owners of a course to edit or delete it.
    Allows read access to authenticated students, teachers, or staff.
    """
    message = "You must be the owner of this course to modify or delete it."

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated user if they are students, teachers, or staff.
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated and \
                   (request.user.role == 'student' or request.user.role == 'teacher' or request.user.is_staff)

        # Write permissions are only allowed to the teacher of the course.
        # Ensure user is authenticated before checking role and ownership.
        return request.user.is_authenticated and \
               request.user.role == 'teacher' and \
               obj.teacher == request.user

class IsEnrollmentOwnerOrCourseTeacher(BasePermission):
    """
    Object-level permission for enrollments:
    - Students can manage their own enrollments.
    - Teachers can manage enrollments for their courses.
    - Admins can also modify.
    Read access (SAFE_METHODS) could be broader if needed, but this focuses on modification.
    """
    message = "You must own this enrollment or be the teacher of the course to modify or delete it."

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        # Admins can do anything with the enrollment object
        if request.user.is_staff:
            return True

        # Student owns the enrollment (can view, delete their own enrollment)
        if request.user.role == 'student' and obj.student == request.user:
            return True

        # Teacher owns the course to which the student is enrolled
        # (can view, potentially delete enrollments from their course)
        if request.user.role == 'teacher' and obj.course.teacher == request.user:
            return True

        return False

class CanEnroll(BasePermission):
    """
    List-level permission for creating new enrollments.
    - Only students can create enrollments (POST).
    - Authenticated users can view lists of enrollments (GET).
    """
    message = "Only students can enroll in courses. Ensure the course is published and you are logged in as a student."

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method == 'POST': # Action: creating an enrollment
            return request.user.role == 'student'

        # For other methods like GET (listing enrollments), allow if authenticated.
        # Specific object-level visibility (e.g., a student seeing only their enrollments,
        # or a teacher seeing enrollments for their courses) will be handled by
        # IsEnrollmentOwnerOrCourseTeacher for detail views or queryset filtering in the ViewSet.
        return True

    # Optional: has_object_permission could be used if there were checks against a specific
    # course object when creating an enrollment (e.g. if this permission was on a
    # course-specific enrollment view like /courses/{course_pk}/enroll/).
    # However, for a general /enrollments/ POST, this is not directly applicable.
    # Course-specific validation (like is_published) is better handled in the EnrollmentSerializer's
    # validate_course method or the view's perform_create.
    # def has_object_permission(self, request, view, obj):
    #     # Example: if 'obj' is the course being enrolled into
    #     if request.method == 'POST': # During enrollment creation
    #         return obj.is_published # Ensure course is published
    #     return True

class IsLiveSessionOwnerAndTeacher(BasePermission):
    """
    Object-level permission to only allow the teacher who created a live session
    to perform actions like starting or ending it.
    """
    message = "You must be the teacher who created this live session to perform this action."

    def has_object_permission(self, request, view, obj): # obj is a LiveSession instance
        if not request.user.is_authenticated or request.user.role != 'teacher':
            return False
        # Check if the authenticated user is the one who created the live session.
        # Assumes 'obj' is a LiveSession instance which has a 'created_by' field.
        return obj.created_by == request.user
