from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

User = get_user_model()

class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    # add_form = UserCreationForm # If you have a custom creation form
    # form = UserChangeForm # If you have a custom change form

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference a username field if it exists.
    list_display = ('email', 'first_name', 'last_name', 'role', 'balance', 'is_staff', 'is_active', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'role', 'balance')}), # Added balance here
        ('Role-specific info', {'fields': ('major', 'department', 'bio')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    # add_fieldsets is used for the user creation page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            # Balance typically starts at 0 and is modified by transactions, not usually set at creation.
            # If it needs to be set at creation by admin, add 'balance' here.
            'fields': ('email', 'password', 'password2', 'first_name', 'last_name', 'role', 'major', 'department', 'bio'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    # Since USERNAME_FIELD is 'email', 'username' is not in fieldsets/list_display by default.
    # Ensure that role-specific fields are present if you want to edit them in admin.
    # The default UserAdmin might not show them.

admin.site.register(User, UserAdmin)
