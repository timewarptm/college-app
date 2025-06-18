from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', _('Student')),
        ('teacher', _('Teacher')),
    )

    # AbstractUser already defines username, first_name, last_name, email, is_staff, is_active, date_joined.
    # We will use email as the primary identifier instead of username.
    username = None # Remove username field
    email = models.EmailField(_('email address'), unique=True, help_text=_('Required. Used for login.'))

    role = models.CharField(
        _('role'),
        max_length=10,
        choices=ROLE_CHOICES,
        help_text=_('User role, determines access and specific profile fields.')
    )

    # Role-specific fields
    major = models.CharField(
        _('major'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Applicable if role is Student.')
    )
    department = models.CharField(
        _('department'),
        max_length=100,
        blank=True,
        null=True,
        help_text=_('Applicable if role is Teacher.')
    )
    bio = models.TextField(
        _('biography'),
        blank=True,
        null=True,
        help_text=_('Applicable if role is Teacher. A short biography.')
    )

    balance = models.DecimalField(
        _("balance"),
        max_digits=12,
        decimal_places=2,
        default=0.00,
        help_text=_("User's internal balance.")
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'role'] # email is already covered by USERNAME_FIELD

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        # Ensure role-specific fields are only populated for the correct role
        if self.role == 'student':
            self.department = None
            self.bio = None
        elif self.role == 'teacher':
            self.major = None
        # If role is not set, or an unexpected value, clear all role-specific fields
        # This case should ideally be prevented by the `choices` on the role field
        elif self.role not in [role_choice[0] for role_choice in self.ROLE_CHOICES]:
            self.major = None
            self.department = None
            self.bio = None


    def save(self, *args, **kwargs):
        self.clean() # Call clean to enforce role-specific field constraints
        super().save(*args, **kwargs)
