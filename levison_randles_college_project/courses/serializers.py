from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Course, Enrollment, LiveSession
# Assuming UserSerializer is in accounts.serializers
# Adjust the import path if your UserSerializer is located elsewhere.
from accounts.serializers import UserSerializer

User = get_user_model()

class TeacherField(serializers.PrimaryKeyRelatedField):
    def to_representation(self, value):
        # Instead of just PK, return a serialized representation of the teacher
        user = User.objects.get(pk=value.pk)
        return UserSerializer(user, context=self.context).data

class CourseSerializer(serializers.ModelSerializer):
    # For read operations, use a nested UserSerializer.
    # For write operations (create/update), allow setting teacher by primary key.
    # We can achieve this by defining two different fields or using a custom field.
    # A simpler approach for now is to have one field that behaves differently for read/write.
    # However, DRF typically uses a single field definition.
    # Let's use PrimaryKeyRelatedField for write and a custom representation for read.

    # teacher = serializers.PrimaryKeyRelatedField(
    #     queryset=User.objects.filter(role='teacher'),
    #     help_text="ID of the teacher for this course."
    # )
    # For more detailed teacher info on read:
    teacher_details = UserSerializer(source='teacher', read_only=True)

    # Alternative for 'teacher' field to allow write by ID and read with details:
    # This is more complex. Using teacher_details for read and teacher (PK) for write is common.
    # For now, we'll have 'teacher' as PK for write, and 'teacher_details' for read.
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='teacher'),
        write_only=True, # This field will only be used for write operations
        help_text="Set the teacher by their User ID. Ensure the user has the 'teacher' role."
    )

    enrolled_students_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = (
            'id', 'title', 'description', 'teacher', 'teacher_details',
            'syllabus', 'is_published',
            'created_at', 'updated_at', 'enrolled_students_count'
        )
        read_only_fields = ('id', 'created_at', 'updated_at', 'teacher_details')
        # 'teacher' is write_only as defined above.

    def get_enrolled_students_count(self, obj):
        return obj.enrolled_students.count()

    def validate_teacher(self, value):
        # Ensure the selected user for teacher has the 'teacher' role.
        # The queryset in PrimaryKeyRelatedField already limits choices,
        # but an explicit validation here is good practice.
        if value.role != 'teacher':
            raise serializers.ValidationError("The assigned user must have the 'teacher' role.")
        return value

class CourseBasicInfoSerializer(serializers.ModelSerializer):
    """A simplified serializer for Course, e.g., for nesting in EnrollmentSerializer."""
    class Meta:
        model = Course
        fields = ('id', 'title') # Add other essential fields if needed


class EnrollmentSerializer(serializers.ModelSerializer):
    # For read operations, use nested serializers for student and course.
    # For write, use PrimaryKeyRelatedField.
    student_details = UserSerializer(source='student', read_only=True)
    course_details = CourseBasicInfoSerializer(source='course', read_only=True)

    student = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role='student'),
        write_only=True, # This field will only be used for write operations
        help_text="Set the student by their User ID. Ensure the user has the 'student' role."
    )
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), # Or filter by is_published=True for student enrollments
        write_only=True, # This field will only be used for write operations
        help_text="Set the course by its ID."
    )

    class Meta:
        model = Enrollment
        fields = (
            'id', 'student', 'student_details', 'course', 'course_details', 'enrolled_at'
        )
        read_only_fields = ('id', 'enrolled_at', 'student_details', 'course_details')
        # 'student' and 'course' are write_only as defined above.

    def validate_student(self, value):
        # Ensure the selected user for student has the 'student' role.
        if value.role != 'student':
            raise serializers.ValidationError("The enrolling user must have the 'student' role.")
        return value

    def create(self, validated_data):
        # Check for unique_together constraint manually before attempting to create,
        # as by default DRF validation for unique_together happens at DB level.
        # This provides a cleaner API error.
        student = validated_data.get('student')
        course = validated_data.get('course')
        if Enrollment.objects.filter(student=student, course=course).exists():
            raise serializers.ValidationError({
                "detail": "This student is already enrolled in this course.",
                "code": "already_enrolled"
            })
        return super().create(validated_data)


class LiveSessionSerializer(serializers.ModelSerializer):
    course_details = CourseBasicInfoSerializer(source='course', read_only=True)
    created_by_details = UserSerializer(source='created_by', read_only=True)

    # For write operations, allow setting course and created_by by primary key.
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all(), # Teachers can only create for courses they teach (handled in view)
        write_only=True
    )
    # created_by will be set automatically from request.user in the view.
    # It's not expected in the request payload for creation by a teacher.
    # If an admin were to create it and assign a teacher, this field might be writable.
    # For now, let's assume it's set in the view.

    class Meta:
        model = LiveSession
        fields = (
            'id', 'course', 'course_details', 'title', 'room_id',
            'status', 'started_at', 'ended_at',
            'created_by', 'created_by_details', 'created_at', 'updated_at'
        )
        read_only_fields = (
            'id', 'room_id', 'status', 'started_at', 'ended_at',
            'created_by', 'created_by_details', 'created_at', 'updated_at',
            'course_details' # Only 'course' (PK) is writable
        )
        # `created_by` is effectively read-only from client perspective as it's set by view.
        # `status`, `started_at`, `ended_at` are managed by specific actions in the view.

    def validate_course(self, value):
        # In a view where the user is creating the session,
        # ensure the course's teacher is the request.user.
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.teacher != request.user and not request.user.is_staff:
                raise serializers.ValidationError(
                    "You can only create live sessions for courses you teach."
                )
        return value
