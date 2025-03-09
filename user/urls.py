from django.urls import path
from .views import OtpGenerateView, OtpConfirmView, update_student_matricule, update_student_face
urlpatterns = [
    path('otp/generate/', OtpGenerateView.as_view(), name='otp-generate'),
    path('otp/confirm/', OtpConfirmView.as_view(), name='otp-confirm'),
    path('student/matricule/update/', update_student_matricule, name='update-student-matricule'),
    path('student/face/update/', update_student_face, name='update-student-face')
]
