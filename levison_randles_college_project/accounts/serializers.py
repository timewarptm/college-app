from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    # Role-specific fields made writable for registration
    major = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True, style={'base_template': 'textarea.html'})

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'role', 'major', 'department', 'bio')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'role': {'required': True},
        }

    def validate_role(self, value):
        """
        Check that the role is one of the available choices.
        """
        valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
        if value not in valid_roles:
            raise serializers.ValidationError(f"Invalid role. Must be one of {valid_roles}.")
        return value

    def validate(self, attrs):
        """
        Validate role-specific fields.
        - If role is 'student', 'major' can be provided, 'department' and 'bio' must be empty.
        - If role is 'teacher', 'department' and 'bio' can be provided, 'major' must be empty.
        """
        role = attrs.get('role')
        major = attrs.get('major')
        department = attrs.get('department')
        bio = attrs.get('bio')

        if role == 'student':
            if department or bio:
                raise serializers.ValidationError({
                    "department": "Department must be empty for students.",
                    "bio": "Bio must be empty for students."
                })
        elif role == 'teacher':
            if major:
                raise serializers.ValidationError({
                    "major": "Major must be empty for teachers."
                })
        # No need to validate if role is not present, as it's a required field and will be caught by default
        return attrs

    def create(self, validated_data):
        # Hash the password before saving
        validated_data['password'] = make_password(validated_data.get('password'))

        # Pop role-specific fields that might not be directly on the User model instance before super().create()
        # if they are handled by the model's clean/save method.
        # However, with our current model, these fields are directly on User.

        user = User.objects.create(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    # Role-specific fields made read-only here, they are managed via registration or profile update logic
    major = serializers.CharField(read_only=True, allow_null=True)
    department = serializers.CharField(read_only=True, allow_null=True)
    bio = serializers.CharField(read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role',
                  'major', 'department', 'bio', 'balance', # Added balance
                  'is_active', 'date_joined', 'last_login')
        read_only_fields = ('is_active', 'date_joined', 'last_login', 'id', 'balance') # Made balance read-only

class UserProfileUpdateSerializer(serializers.ModelSerializer):
    # Allows updating common fields and role-specific fields
    # Role itself is not updatable here, typically role changes are administrative actions
    major = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    department = serializers.CharField(max_length=100, required=False, allow_blank=True, allow_null=True)
    bio = serializers.CharField(required=False, allow_blank=True, allow_null=True, style={'base_template': 'textarea.html'})

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'major', 'department', 'bio')
        # Email is not included here as changing email (USERNAME_FIELD) often has security implications
        # and might need a separate flow (e.g., email verification).

    def validate(self, attrs):
        user = self.instance # User instance during an update
        if not user:
            # This case should ideally not be hit if serializer is used correctly in a view
            raise serializers.ValidationError("User instance not found for validation.")

        role = user.role # Get the existing role of the user

        major = attrs.get('major', user.major) # Use new value if provided, else existing
        department = attrs.get('department', user.department)
        bio = attrs.get('bio', user.bio)

        if role == 'student':
            # If new department or bio is provided for a student, it's an error
            if attrs.get('department') is not None or attrs.get('bio') is not None:
                 raise serializers.ValidationError("Students cannot set department or bio.")
            attrs['department'] = None # Ensure these are cleared if student updates other fields
            attrs['bio'] = None
        elif role == 'teacher':
            # If new major is provided for a teacher, it's an error
            if attrs.get('major') is not None:
                raise serializers.ValidationError("Teachers cannot set a major.")
            attrs['major'] = None # Ensure major is cleared if teacher updates other fields
        return attrs

    def update(self, instance, validated_data):
        # The model's save() method which calls clean() will handle None-ing out
        # fields not relevant to the role.
        return super().update(instance, validated_data)
