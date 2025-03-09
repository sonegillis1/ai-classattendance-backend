from django.db import models
from user.models import Student  # Ensure you import the necessary models

# Create your models here.

class Course(models.Model):
    title = models.CharField(max_length=100)  # Course title
    code = models.CharField(max_length=10)    # Course code
    
    def __str__(self):
        return self.title
    

class CourseTeacher(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Reference to the Course model
    teacher = models.ForeignKey('user.Teacher', on_delete=models.CASCADE)  # Reference to the Teacher model
    is_primary = models.BooleanField(default=False)  # Indicates if the teacher is the primary teacher for the course
    
    class Meta:
        unique_together = ('course', 'is_primary')  # Ensure only one primary teacher per course

    def __str__(self):
        return f"{self.course.code} - {self.teacher.user.email}"  # Mixture of course code and teacher email


class Attendance(models.Model):
    teacher = models.ForeignKey('user.Teacher', on_delete=models.CASCADE)  # Reference to the Teacher model
    course = models.ForeignKey(Course, on_delete=models.CASCADE)  # Reference to the Course model
    date = models.DateField(auto_created=True)  # Date of the attendance

    def __str__(self):
        return f"{self.course.code} - {self.date} - {self.teacher.email}"  # Mixture of course code, date, and teacher email


class AttendanceRecord(models.Model):
    attendance = models.ForeignKey(Attendance, on_delete=models.CASCADE)  # Reference to the Attendance model
    student = models.ForeignKey('user.Student', on_delete=models.CASCADE)  # Reference to the Student model

    def __str__(self):
        return f"{self.attendance} - {self.student.email} - {'Present' if self.present else 'Absent'}"  # Attendance info and student email


class StudentCourseRegistration(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student} registered for {self.course}"





