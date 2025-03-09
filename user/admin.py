from django.contrib import admin
from .models import FaceRegistrationImage, Teacher, Student, LoginCode

# Register your models here.
@admin.register(FaceRegistrationImage)
class FaceRegistrationImageAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('user', 'title')
    search_fields = ('user__email', 'title')

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'matricule')
    search_fields = ('user__email', 'matricule')

@admin.register(LoginCode)
class LoginCodeAdmin(admin.ModelAdmin):
    list_display = ('user', 'code', 'created_at')
    search_fields = ('user__email', 'code')
