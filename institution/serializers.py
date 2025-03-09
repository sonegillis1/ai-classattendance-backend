from rest_framework import serializers

from institution.models import Course, CourseTeacher, StudentCourseRegistration  # Import serializers

class CourseSerializer(serializers.ModelSerializer):  # Serializer for Course model
    class Meta:
        model = Course
        fields = '__all__'  # Include all fields in the serializer

class CourseTeacherSerializer(serializers.ModelSerializer):  # Serializer for CourseTeacher model
    class Meta:
        model = CourseTeacher
        fields = '__all__'  # Include all fields in the serializer


class StudentCourseRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentCourseRegistration
        fields = ['student', 'course', 'date']  # Specify the fields to include in the serializer
