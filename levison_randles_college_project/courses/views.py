from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Course, Enrollment, LiveSession
from .serializers import CourseSerializer, EnrollmentSerializer, LiveSessionSerializer
from .permissions import (
    IsTeacher, IsStudent, IsCourseOwner,
    IsEnrollmentOwnerOrCourseTeacher, CanEnroll, IsLiveSessionOwnerAndTeacher # Import new permission
)

class CourseViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows courses to be viewed or edited.
    - Teachers can create, update, delete, publish/unpublish their courses.
    - Students and other authenticated users can view published courses.
    """
    serializer_class = CourseSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'teacher' or user.is_staff:
                # Teachers and staff can see all courses (published or not)
                # Potentially, teachers might only see their own unpublished courses unless staff
                if user.is_staff:
                    return Course.objects.all()
                return Course.objects.filter(teacher=user) | Course.objects.filter(is_published=True) # Own courses + published
            # Students see only published courses
            return Course.objects.filter(is_published=True)
        return Course.objects.filter(is_published=True) # Unauthenticated users see published courses

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action == 'create':
            self.permission_classes = [IsTeacher]
        elif self.action in ['update', 'partial_update', 'destroy', 'publish', 'unpublish']:
            self.permission_classes = [IsCourseOwner]
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.IsAuthenticatedOrReadOnly] # Allow anon read for published
        else:
            self.permission_classes = [permissions.IsAdminUser] # Default to admin for other actions
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsCourseOwner])
    def publish(self, request, pk=None):
        course = self.get_object()
        if course.teacher != request.user and not request.user.is_staff:
             return Response({'detail': 'You are not the teacher of this course.'}, status=status.HTTP_403_FORBIDDEN)
        course.is_published = True
        course.save()
        return Response({'status': 'course published'}, serializer.data)

    @action(detail=True, methods=['post'], permission_classes=[IsCourseOwner])
    def unpublish(self, request, pk=None):
        course = self.get_object()
        if course.teacher != request.user and not request.user.is_staff:
            return Response({'detail': 'You are not the teacher of this course.'}, status=status.HTTP_403_FORBIDDEN)
        course.is_published = False
        course.save()
        return Response({'status': 'course unpublished'}, serializer.data)


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing student enrollments.
    - Students can create (enroll) and delete (unenroll) their own enrollments.
    - Teachers can view enrollments for their courses.
    - Staff can view all enrollments.
    """
    serializer_class = EnrollmentSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Enrollment.objects.none()

        if user.is_staff:
            return Enrollment.objects.all()
        elif user.role == 'student':
            return Enrollment.objects.filter(student=user)
        elif user.role == 'teacher':
            return Enrollment.objects.filter(course__teacher=user)
        return Enrollment.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [CanEnroll] # Checks for student role
        elif self.action == 'destroy':
            self.permission_classes = [IsEnrollmentOwnerOrCourseTeacher]
        elif self.action in ['list', 'retrieve']:
            # Basic auth check, actual data visibility is handled by get_queryset
            self.permission_classes = [permissions.IsAuthenticated]
        else: # 'update', 'partial_update' are not typically used for enrollments.
            self.permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        course = serializer.validated_data.get('course')
        if not course.is_published:
            # This check can also be added to EnrollmentSerializer's validate_course
            raise serializers.ValidationError("Cannot enroll in an unpublished course.")
        serializer.save(student=self.request.user)


class CourseEnrollmentListView(generics.ListAPIView):
    """
    API endpoint to list students enrolled in a particular course.
    Accessible by the teacher of the course or staff.
    """
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsCourseOwner] # IsCourseOwner checks teacher

    def get_queryset(self):
        course_pk = self.kwargs['course_pk']
        course = get_object_or_404(Course, pk=course_pk)

        # Check permissions for the course object itself using IsCourseOwner logic
        # This is a bit manual here as generics.ListAPIView doesn't call check_object_permissions by default
        # for the main object (the course in this case).
        # A simpler way if IsCourseOwner is adapted or view is part of CourseViewSet:
        # self.check_object_permissions(self.request, course)

        user = self.request.user
        if not (user.is_staff or (user.role == 'teacher' and course.teacher == user)):
            return Enrollment.objects.none() # Return empty if user is not owner/staff

        return Enrollment.objects.filter(course=course)

    def get_permissions(self):
        # For CourseEnrollmentListView, the main permission is about accessing the list.
        # The IsCourseOwner check here is more about whether the user is authorized for the *course* itself.
        # We need to manually instantiate IsCourseOwner and check permission against the course.
        # This is a bit of a workaround because generics.ListAPIView doesn't have a `self.get_object()` that
        # IsCourseOwner would typically use.
        # A cleaner way might be to integrate this as an action on CourseViewSet.

        # For now, the permission_classes attribute handles it if IsCourseOwner is adapted
        # to work without obj for has_permission, or if we fetch course and check manually.
        # The IsCourseOwner in permission_classes will be called by DRF.
        # If it needs an object for has_object_permission, we must ensure it gets the course.
        # This is tricky with generics.ListAPIView.
        # Let's rely on the get_queryset to filter appropriately for now,
        # and IsCourseOwner on the view will primarily check if the user is a teacher
        # and then get_queryset confirms if they own *this* course.

        # Simplified: a teacher should be able to list enrollments for a course they own.
        # We can rely on the get_queryset to enforce this.
        # IsTeacher permission would be more direct for has_permission if we check ownership in get_queryset.

        # Let's adjust the main permission_classes for this view to be [IsTeacher]
        # and then get_queryset will ensure it's *their* course.
        # This is simpler than making IsCourseOwner work without an object initially.

        # Re-evaluating: The permission_classes on the view are checked first.
        # IsCourseOwner as defined needs an object.
        # A simpler approach for THIS specific view:
        if self.request.method == 'GET': # Only GET is relevant for ListAPIView
            return [permission() for permission in [permissions.IsAuthenticated, IsTeacher]] # Must be a teacher
        return [permission() for permission in self.permission_classes]


# To make CourseEnrollmentListView work correctly with IsCourseOwner,
# IsCourseOwner's has_permission would need to be adapted, or this view
# needs to fetch the course object earlier in dispatch and have check_object_permissions called.
# The current get_queryset is doing the effective check for ownership.
# So, [IsTeacher] is sufficient for the view-level permission, and get_queryset handles object-level.

# Let's refine CourseEnrollmentListView's permissions:
# We'll keep IsCourseOwner but it implies the get_queryset will fetch the course,
# and the permission will be checked against that course instance.
# For ListAPIView, has_permission is called. has_object_permission is not called for the list itself.
# So IsCourseOwner might not work as expected if it relies solely on has_object_permission.

# A better permission for CourseEnrollmentListView would be:
class IsTeacherAndOwnsCourseForEnrollmentList(permissions.BasePermission):
    message = "You must be the teacher of this course to view its enrollments."
    def has_permission(self, request, view):
        if not (request.user.is_authenticated and request.user.role == 'teacher'):
            return False
        course_pk = view.kwargs.get('course_pk')
        if not course_pk: return False # Should not happen with correct URL conf
        course = get_object_or_404(Course, pk=course_pk)
        return course.teacher == request.user

# Update CourseEnrollmentListView to use this new permission
CourseEnrollmentListView.permission_classes = [IsTeacherAndOwnsCourseForEnrollmentList]


class LiveSessionViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing live sessions.
    - Teachers can create, start, and end live sessions for their courses.
    - Enrolled students can view active/upcoming live sessions for their courses.
    """
    serializer_class = LiveSessionSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return LiveSession.objects.none()

        if user.is_staff:
            return LiveSession.objects.all()

        # Teachers see live sessions for courses they teach
        if user.role == 'teacher':
            return LiveSession.objects.filter(course__teacher=user)

        # Students see live sessions for courses they are enrolled in
        if user.role == 'student':
            enrolled_course_ids = Enrollment.objects.filter(student=user).values_list('course_id', flat=True)
            return LiveSession.objects.filter(course_id__in=enrolled_course_ids, status__in=['pending', 'live'])
            # Optionally, also show recently ended sessions:
            # from django.utils import timezone
            # from datetime import timedelta
            # recently_ended_cutoff = timezone.now() - timedelta(hours=2)
            # return LiveSession.objects.filter(
            #    course_id__in=enrolled_course_ids,
            #    status__in=['pending', 'live', 'ended']
            # ).filter(
            #    models.Q(status__in=['pending', 'live']) | models.Q(ended_at__gte=recently_ended_cutoff)
            # ).distinct()

        return LiveSession.objects.none()

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = [IsTeacher]
        elif self.action in ['update', 'partial_update', 'destroy']: # Standard ModelViewSet actions
            self.permission_classes = [IsLiveSessionOwnerAndTeacher]
        elif self.action in ['start_session', 'end_session']: # Custom actions
            self.permission_classes = [IsLiveSessionOwnerAndTeacher]
        elif self.action in ['list', 'retrieve']:
            self.permission_classes = [permissions.IsAuthenticated] # Students or Teachers can view
        else:
            self.permission_classes = [permissions.IsAdminUser]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        # `created_by` is set to the request user (must be a teacher due to permissions)
        # `room_id` is generated by default in the model.
        # `status` defaults to 'pending'.
        # `course` is validated in the serializer to ensure teacher owns it.
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='start', permission_classes=[IsLiveSessionOwnerAndTeacher])
    def start_session(self, request, pk=None):
        live_session = self.get_object()
        # Permission class IsLiveSessionOwnerAndTeacher already checks if request.user is obj.created_by

        if live_session.status == 'pending':
            live_session.status = 'live'
            live_session.started_at = timezone.now()
            live_session.save()
            return Response(LiveSessionSerializer(live_session).data)
        return Response({'detail': 'Session is not pending or already started.'}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='end', permission_classes=[IsLiveSessionOwnerAndTeacher])
    def end_session(self, request, pk=None):
        live_session = self.get_object()
        # Permission class IsLiveSessionOwnerAndTeacher already checks if request.user is obj.created_by

        if live_session.status == 'live':
            live_session.status = 'ended'
            live_session.ended_at = timezone.now()
            live_session.save()
            return Response(LiveSessionSerializer(live_session).data)
        return Response({'detail': 'Session is not live or already ended.'}, status=status.HTTP_400_BAD_REQUEST)

# TODO: Refine LiveSessionViewSet permissions for update/destroy/start/end actions
# to use a proper object-level permission like:
# class IsLiveSessionCourseTeacher(BasePermission): # This was the old TODO name
#     def has_object_permission(self, request, view, obj):
#         return request.user.is_authenticated and \
#                request.user.role == 'teacher' and \
#                obj.course.teacher == request.user # This checks course teacher, not session creator
# The new IsLiveSessionOwnerAndTeacher correctly checks obj.created_by.
# The get_permissions method was also updated for standard actions like update/destroy.
