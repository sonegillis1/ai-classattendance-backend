from datetime import datetime
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from institution.tasks import process_video
from user.models import Student, Teacher
from .models import Attendance, Course, CourseTeacher, StudentCourseRegistration, AttendanceRecord  # Assuming you have a Course model
from .serializers import CourseSerializer  # Assuming you have a CourseSerializer

import os
from django.core.files.storage import default_storage

# Create your views here.
class TeacherCoursesViewSet(viewsets.ViewSet):
    def list(self, request, teacher_id=None):
        teacher = Teacher.objects.get(user=request.user)
        courses = CourseTeacher.objects.filter(teacher=teacher).select_related('course')  # Get Course objects related to the teacher
        courses = [course_teacher.course for course_teacher in courses]  # Extract Course objects from CourseTeacher queryset
        print(courses)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)


@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])  # Adjust permissions as needed
def initiate_attendance(request):
    video = request.FILES.get("video")  # Get the video from request
    course_code = request.data.get("course_code")  # Get course code

    if not video or not course_code:
        return Response({"error": "Please provide both a video and a course code."}, status=400)

    # Save the uploaded video temporarily
    video_path = os.path.join("media", f"attendance_videos/${course_code}/{datetime.now()}")
    with default_storage.open(video_path, "wb+") as destination:
        for chunk in video.chunks():
            destination.write(chunk)

    try:
        # Retrieve the course and teacher
        course = Course.objects.get(code=course_code)
        teacher = Teacher.objects.get(user=request.user)

        # Create an Attendance record
        attendance = Attendance.objects.create(course=course, teacher=teacher)

        registrations = StudentCourseRegistration.objects.filter(course__code=course_code).select_related('student')

        # Create the desired dictionary structure
        students_embeddings = {}
        for registration in registrations:
            student = registration.student
            students_embeddings[student.matricule] = {
                "frontal": student.frontal_face_embedding,
                "left": student.left_face_embedding,
                "right": student.right_face_embedding,
                "found": False
            }

        # Send the video for processing via Celery
        registered_students = Student.objects.filter(course=course)
        task = process_video.delay(attendance, video_path, students_embeddings)

        return Response({"message": "Processing attendance", "task_id": task.id}, status=200)

    except Course.DoesNotExist:
        return Response({"error": "Invalid course code."}, status=400)
    except Teacher.DoesNotExist:
        return Response({"error": "Teacher not found."}, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])  # Adjust permissions as needed
def get_attendance(request):
    date = request.query_params.get("date")  # Get the date from query parameters
    course_code = request.query_params.get("course_code")  # Get course code

    if not date or not course_code:
        return Response({"error": "Please provide both a date and a course code."}, status=400)

    try:
        # Retrieve the course
        course = Course.objects.get(code=course_code)

        # Get attendance records for the specified date
        attendance = Attendance.objects.filter(course=course, date=date)
        print('#######', attendance);
        if attendance.exists():
            attendance_records = AttendanceRecord.objects.filter(attendance=attendance)

            # Get registered students for the course
            registrations = StudentCourseRegistration.objects.filter(course=course).select_related('student')

            # Create a dictionary to hold attendance status
            attendance_status = {registration.student.matricule: {"present": False} for registration in registrations}

            # Mark students as present if they are in the attendance records
            for record in attendance_records:
                attendance_status[record.student.matricule]["present"] = True
            print(attendance_status)
            return Response(attendance_status, status=200)
        return Response([], status=200)

    except Course.DoesNotExist:
        return Response({"error": "Invalid course code."}, status=400)


