from django.contrib import admin
from .models import Course, Enrollment

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'teacher', 'is_published', 'created_at', 'updated_at')
    list_filter = ('is_published', 'teacher')
    search_fields = ('title', 'description', 'teacher__email', 'teacher__first_name', 'teacher__last_name')
    autocomplete_fields = ['teacher'] # Assuming UserAdmin has search_fields configured

    fieldsets = (
        (None, {'fields': ('title', 'description', 'teacher')}),
        ('Details', {'fields': ('syllabus', 'is_published')}),
    )

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'enrolled_at')
    list_filter = ('course', 'student') # Consider if student filter is too long
    search_fields = ('student__email', 'student__first_name', 'course__title')
    autocomplete_fields = ['student', 'course']

    # To make student and course fields searchable for autocomplete,
    # ensure their respective UserAdmin and CourseAdmin have search_fields defined.
    # For UserAdmin, we already configured this in the accounts app.
