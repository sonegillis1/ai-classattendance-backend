from rest_framework import serializers
from .models import Student, LoginCode, Teacher

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = '__all__'  # Include all fields

class LoginCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoginCode
        fields = '__all__'  # Include all fields 

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['title', 'profile_pic'] 