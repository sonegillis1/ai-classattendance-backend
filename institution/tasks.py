import cv2
from celery import shared_task

from ai.video_face_recognition import detect_faces
from institution.models import Student, AttendanceRecord


@shared_task
def process_video(attendance, video_path, student_embeddings):
    """
    Celery task to process a video file and detect faces frame-by-frame.
    
    Args:
    - video_path (str): Path to the video file.
    
    Returns:
    - List of detected faces per frame.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {"error": "Cannot open video file"}

    all_faces = []  # Store detected faces

    while True:
        ret, frame = cap.read()
        if not ret:
            break  # End of video

        faces = detect_faces(student_embeddings, frame)
        all_faces.extend(faces)
    
    cap.release()
    all_faces = set(all_faces)

    # Create attendance records for each detected face
    for matricule in all_faces:
        # Assuming you have a method to get the student by matricule
        try:
            student = Student.objects.get(matricule=matricule)  # Fetch student by matricule
            AttendanceRecord.objects.create(attendance=attendance, student=student)  # Create attendance record
        except Student.DoesNotExist:
            continue  # Skip if student does not exist

    return all_faces
