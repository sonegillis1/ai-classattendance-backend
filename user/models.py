from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class FaceRegistrationImage(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    front_face = models.ImageField(upload_to='face_images/front/', blank=True, null=True)
    left_face = models.ImageField(upload_to='face_images/left/', blank=True, null=True)
    right_face = models.ImageField(upload_to='face_images/right/', blank=True, null=True)

    # New fields for face embeddings
    front_face_embedding = models.BinaryField(null=True, blank=True)
    left_face_embedding = models.BinaryField(null=True, blank=True)
    right_face_embedding = models.BinaryField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Face Registration for {self.user.username}"


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # One-to-one mapping with User model
    title = models.CharField(max_length=100)  # Teacher's title
    profile_pic = models.ImageField(upload_to='profile_pics/', null=True, blank=True)  # Teacher's profile picture

    def __str__(self):
        return f"{self.title} {self.user.email}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    matricule = models.CharField(max_length=20, unique=True)
    
    # New fields for face embeddings
    frontal_face_embedding = models.BinaryField(null=True, blank=True)
    left_face_embedding = models.BinaryField(null=True, blank=True)
    right_face_embedding = models.BinaryField(null=True, blank=True)
    
    def __str__(self) -> str:
        return f"{self.user.email}"


class LoginCode(models.Model):
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
