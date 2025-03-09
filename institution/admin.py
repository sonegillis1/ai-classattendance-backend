from django.contrib import admin
from .models import Course, CourseTeacher, Attendance, AttendanceRecord, StudentCourseRegistration

# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'code')  # Display title and code in the admin list view

@admin.register(CourseTeacher)
class CourseTeacherAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher', 'is_primary')  # Display course, teacher, and primary status

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher', 'date')  # Display these fields in the admin list view

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ('attendance', 'student')  # Display these fields in the admin list view

@admin.register(StudentCourseRegistration)
class StudentCourseRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'date')  # Specify fields to display in the admin list view
    search_fields = ('student__name', 'course__name')  # Enable search by student and course names
