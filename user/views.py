from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes, api_view
from rest_framework import status
import random
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

from ai.extract_embedding import extract_embeddings
from ai.face_detection_and_orientation import detect_face_and_orientation
from ai.tasks import detect_face_and_find_orientation_task
from common.constants.shared import CACHE_KEY_AUTHENTICATION_CODE

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from user.models import FaceRegistrationImage, Student, Teacher
from user.serializers import TeacherSerializer
from user.utils import generate_user_token, send_otp_email

import os

# Create your views here.

class OtpGenerateView(APIView):
    @swagger_auto_schema(
        operation_description="Generate OTP With User Email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description=f'Institutional email address e.g student{settings.INSTITUTIONAL_EMAIL_SUFFIX}')
            }
        ),
        responses={
            201: openapi.Response(
                description='Code Generated',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @csrf_exempt
    def post(self, request):
        data = request.data
        email = data.get('email')
        if not email or not email.endswith(settings.INSTITUTIONAL_EMAIL_SUFFIX):
            return Response({'message': f'Use an institutional email e.g {settings.INSTITUTIONAL_EMAIL_SUFFIX}'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Generate an 6-digit code
        code = str(random.randint(100000, 999999))
        print('code is ', code)
        cache.set(f'{CACHE_KEY_AUTHENTICATION_CODE}{email}', code, settings.CACHE_AUTHENTICATION_CODE_TIMEOUT)
        send_otp_email(email.lower(), code)
        return Response({'message': 'Code generated', 'code': code}, status=status.HTTP_201_CREATED)

class OtpConfirmView(APIView):
    @swagger_auto_schema(
        operation_description="Confirm OTP With User Email",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'otp'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description=f'Institutional email address e.g student{settings.INSTITUTIONAL_EMAIL_SUFFIX}'),
                'otp': openapi.Schema(type=openapi.TYPE_INTEGER, description="OTP Sent to user's email")
            }
        ),
        responses={
            200: openapi.Response(
                description='Code Generated',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            ),
            400: openapi.Response(
                description='Bad Request',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'message': openapi.Schema(type=openapi.TYPE_STRING)
                    }
                )
            )
        }
    )
    @csrf_exempt
    def post(self, request):
        data = request.data
        email = data['email']
        code = data['otp']

        if not email or not email.endswith(settings.INSTITUTIONAL_EMAIL_SUFFIX):
            return Response({'message': f'Use an institutional email e.g {settings.INSTITUTIONAL_EMAIL_SUFFIX}'}, status=status.HTTP_400_BAD_REQUEST)
        
        cache_code = cache.get(f'{CACHE_KEY_AUTHENTICATION_CODE}{email}')
        print(f'######## cache code ', code)
        if cache_code == code:
            user, created = User.objects.get_or_create(username=email.lower(), email=email.lower())
            refresh = generate_user_token(user)

            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }, status=status.HTTP_200_OK)
        return Response({'message': f'Code expired or not found'}, status=status.HTTP_401_UNAUTHORIZED)
    

@csrf_exempt
@permission_classes([IsAuthenticated])
@api_view(['POST'])
def update_student_face(request):
    face_direction = request.data['direction']
    uploaded_image = request.FILES.get('face_image')
    face_direction_map = {
        "frontal": 0,
        "left": -1,
        "right": 1
    }
    print(uploaded_image, face_direction);
    import numpy as np
    import cv2
    if uploaded_image and face_direction:
        # Read the image file into a numpy array
        file_bytes = np.asarray(bytearray(uploaded_image.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        # Check if the image was loaded successfully
        if image is None:
            return Response({'message': 'Image could not be loaded'}, status=status.HTTP_400_BAD_REQUEST)
        # detect_face_and_find_orientation_task.delay(image, face_direction)
        detected, found_direction, cropped = detect_face_and_orientation(image)

        if detected == 0:
            return Response({'message': f'Face not detected'}, status=status.HTTP_400_BAD_REQUEST) 
        elif detected == -1:
            return Response({'message': f'More than one face detected in image'}, status=status.HTTP_400_BAD_REQUEST)
        
        if face_direction_map[face_direction] != found_direction:
             return Response({'message': f'Image does not capture {face_direction}'}, status=status.HTTP_400_BAD_REQUEST)
        
        embedding = extract_embeddings(cropped)
        # Construct a relative path for the saved image
        relative_face_image_path = f"face_images/{face_direction}/{request.user.email}_{face_direction}.png"
        face_image_path = os.path.join(settings.MEDIA_ROOT, relative_face_image_path)

        os.makedirs(os.path.dirname(face_image_path), exist_ok=True)
        is_saved = cv2.imwrite(face_image_path, cropped)  # Save the cropped image
        print(f'Face direction image saved at: {face_image_path}, is saved {is_saved}')

        # Create or get the FaceRegistrationImage instance
        face_registration_image, created = FaceRegistrationImage.objects.get_or_create(
            user=request.user,
            defaults={
                'front_face': relative_face_image_path if face_direction == "frontal" else None,
                'left_face': relative_face_image_path if face_direction == "left" else None,
                'right_face': relative_face_image_path if face_direction == "right" else None,
                'front_face_embedding': embedding.tobytes() if face_direction == "frontal" else None,
                'left_face_embedding': embedding.tobytes() if face_direction == "left" else None,
                'right_face_embedding': embedding.tobytes() if face_direction == "right" else None,
            }
        )

        if not created:
            # If the instance already exists, update the relevant fields
            if face_direction == "frontal":
                face_registration_image.front_face = relative_face_image_path
                face_registration_image.front_face_embedding = embedding.tobytes()
            elif face_direction == "left":
                face_registration_image.left_face = relative_face_image_path
                face_registration_image.left_face_embedding = embedding.tobytes()
            elif face_direction == "right":
                face_registration_image.right_face = relative_face_image_path
                face_registration_image.right_face_embedding = embedding.tobytes()
            face_registration_image.save()

        refresh = generate_user_token(request.user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        })

    return Response({'message': f'Image and face direction are required'}, status=status.HTTP_400_BAD_REQUEST)



@csrf_exempt
@permission_classes([IsAuthenticated])
@api_view(['POST'])
@swagger_auto_schema(
    operation_description="Create Student Profile with matricule",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['matricule'],
        properties={
            'matricule': openapi.Schema(type=openapi.TYPE_STRING, description='Matricule number'),
        }
    ),
    responses={
        200: openapi.Response(
            description='Matricule number saved successfully',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'data': openapi.Schema(type=openapi.TYPE_OBJECT, properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token')
                    })
                }
            )
        ),
        400: openapi.Response(
            description='Bad Request',
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING)
                }
            )
        )
    }
)
def update_student_matricule(request):
    matricule = request.data.get('matricule')
    if not matricule:
        return Response({'message': f'Matricule number is required'}, status=status.HTTP_400_BAD_REQUEST)
    student, created = Student.objects.get_or_create(user=request.user)
    student.matricule = matricule
    student.save()
    refresh = generate_user_token(request.user)

    return Response({
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    })
        


# class CreateStudentView(APIView):
#     @csrf_exempt
#     def post(self, request):
#         data = request.data
#         code = data.get('code')
        
#         # Retrieve the student data from Redis
#         student_data = redis_client.get(code)
        
#         if student_data:
#             student_info = json.loads(student_data)
#             matricule = student_info['matricule']
#             email = student_info['email']
            
#             # Here you would typically save the student to the database
#             # For example: Student.objects.create(matricule=matricule, email=email)

#             # Optionally, delete the code from Redis after use
#             redis_client.delete(code)

#             return Response({'message': 'Student created', 'matricule': matricule, 'email': email}, status=status.HTTP_201_CREATED)
#         else:
#             return Response({'message': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)
