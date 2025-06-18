from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .serializers import RegisterSerializer, UserSerializer, UserProfileUpdateSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    View for user registration.
    Creates a new user instance.
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny] # Anyone can register

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    View for retrieving and updating the profile of the authenticated user.
    GET: Returns the profile of the current user.
    PUT/PATCH: Updates the profile of the current user.
    """
    serializer_class = UserSerializer # Default for GET
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Returns the currently authenticated user
        return self.request.user

    def get_serializer_class(self):
        """
        Return the serializer class to use for the request.
        Uses UserProfileUpdateSerializer for PUT/PATCH requests.
        """
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserSerializer # Default for GET

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # After update, return the full user representation using UserSerializer
        # This ensures that read-only fields and the complete object structure are returned
        return Response(UserSerializer(instance, context=self.get_serializer_context()).data)

    def perform_update(self, serializer):
        serializer.save()

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

class LoginView(ObtainAuthToken):
    """
    View for user login.
    Authenticates a user and returns an auth token, user ID, email, and role.
    """
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'role': user.role  # Assuming 'role' is a field on your custom User model
        })
