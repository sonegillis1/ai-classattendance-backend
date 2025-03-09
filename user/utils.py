from django.contrib.auth.models import User
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

import random

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Student, Teacher, FaceRegistrationImage
from .serializers import TeacherSerializer


def generate_user_token(user: User):
    refresh = RefreshToken.for_user(user)
    user_data = {
        "email": user.email,
        "student": None,
        "teacher": None
    }
    student = Student.objects.filter(user=user)
    teacher = Teacher.objects.filter(user=user)
    if student.exists():
        user_data['student'] = {}
        face_registration = FaceRegistrationImage.objects.filter(user=user)

        if face_registration.exists():
            face = face_registration.first()
            if face.front_face:
                user_data['student']['front_face'] = face.front_face.url
            if face.left_face:
                user_data['student']['left_face'] = face.left_face.url
            if face.right_face:
                user_data['student']['right_face'] = face.right_face.url
        user_data['student']['matricule'] = student.first().matricule
    if teacher.exists():
        user_data['teacher'] = TeacherSerializer(teacher.first()).data
    refresh['user_data'] = user_data
    print(refresh)
    return refresh


def send_otp_email(recipient_email, otp):
    subject = "Your AI Attendance Signin Code"
    
    # Render the email template with the dynamic OTP
    html_message = render_to_string('emails/otp_email.html', {'otp': otp})
    
    # Send email
    email = EmailMultiAlternatives(
        subject,
        "Your OTP is: {}".format(otp),  # Fallback plain text version
        settings.DEFAULT_FROM_EMAIL,  # Sender email
        [recipient_email],  # Recipient email
    )
    email.attach_alternative(html_message, "text/html")  # Attach the HTML content
    email.send()
    
