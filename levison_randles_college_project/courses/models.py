from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Course(models.Model):
    title = models.CharField(_("title"), max_length=200)
    description = models.TextField(_("description"))
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, # Or models.SET_NULL if a course can exist without a teacher
        related_name='courses_taught',
        limit_choices_to={'role': 'teacher'},
        help_text=_("The teacher offering this course.")
    )
    syllabus = models.TextField(_("syllabus"), blank=True, help_text=_("Course syllabus or outline."))
    is_published = models.BooleanField(
        _("is published"),
        default=False,
        help_text=_("Whether the course is visible to students.")
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Course")
        verbose_name_plural = _("Courses")
        ordering = ['title']

class Enrollment(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='enrollments',
        limit_choices_to={'role': 'student'},
        help_text=_("The student enrolled in the course.")
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrolled_students', # This gives access to Enrollment objects from Course
        help_text=_("The course the student is enrolled in.")
    )
    enrolled_at = models.DateTimeField(_("enrolled at"), auto_now_add=True)

    def __str__(self):
        return f"{self.student} enrolled in {self.course}"

    class Meta:
        verbose_name = _("Enrollment")
        verbose_name_plural = _("Enrollments")
        unique_together = ('student', 'course') # Ensures a student can only enroll once in the same course
        ordering = ['-enrolled_at']

import uuid

class LiveSession(models.Model):
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('live', _('Live')),
        ('ended', _('Ended')),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='live_sessions',
        help_text=_("The course this live session belongs to.")
    )
    title = models.CharField(_("title"), max_length=200, help_text=_("Title of the live session (e.g., Week 5 Lecture)."))
    room_id = models.CharField(
        _("room ID"),
        max_length=255, # UUIDs are typically 36 chars, but allow for other schemes
        unique=True,
        default=uuid.uuid4, # Generate a UUID by default
        editable=False, # Usually not edited directly
        help_text=_("Unique ID for the WebRTC room/session.")
    )
    status = models.CharField(
        _("status"),
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        help_text=_("Current status of the live session.")
    )
    started_at = models.DateTimeField(_("started at"), null=True, blank=True)
    ended_at = models.DateTimeField(_("ended at"), null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # If teacher account is deleted, session might still be relevant
        null=True,
        related_name='created_live_sessions',
        limit_choices_to={'role': 'teacher'}, # Only teachers can create sessions
        help_text=_("The teacher who initiated this live session.")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} for {self.course.title} ({self.status})"

    class Meta:
        verbose_name = _("Live Session")
        verbose_name_plural = _("Live Sessions")
        ordering = ['-created_at']
