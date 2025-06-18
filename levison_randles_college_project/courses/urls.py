from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, StudentEnrollmentViewSet, CourseEnrollmentListView, LiveSessionViewSet

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'enrollments', StudentEnrollmentViewSet, basename='enrollment')
router.register(r'live-sessions', LiveSessionViewSet, basename='livesession')

# urlpatterns will be built from the router and any custom paths
urlpatterns = [
    path('', include(router.urls)),
    # Custom path for listing enrollments for a specific course
    path('courses/<int:course_pk>/enrollments/', CourseEnrollmentListView.as_view(), name='course-enrollment-list'),
]
