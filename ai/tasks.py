from celery import shared_task
from ai.face_detection_and_orientation import detect_face_and_orientation

@shared_task
def detect_face_and_find_orientation_task(image, direction):
    detected, found_direction, cropped = detect_face_and_orientation(image)
    print.log('########## result ', detected, found_direction, cropped)
