from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import initiate_attendance, TeacherCoursesViewSet, get_attendance

router = DefaultRouter()
router.register(r'courses', TeacherCoursesViewSet, basename='teacher-courses')

urlpatterns = [
    path('attendance/', initiate_attendance, name='initiate-attendance'),
    path('attendance-list/', get_attendance, name='attendance-list'),
    path('', include(router.urls)),
]
