import cv2
from mtcnn import MTCNN
import numpy as np
import torch

from ai.extract_embedding import extract_embeddings

detector = MTCNN()

def compare_faces_torch(embedding1, embedding2, threshold=0.6):
    """
    Compare two face embeddings using PyTorch Cosine Similarity.
    
    Args:
    - embedding1: First face embedding (1D PyTorch tensor).
    - embedding2: Second face embedding (1D PyTorch tensor).
    - threshold: Minimum similarity for a match (default = 0.6).
    
    Returns:
    - True if faces match, False otherwise.
    - Similarity score.
    """
    embedding1 = embedding1.unsqueeze(0)  # Ensure 2D shape (1, 512)
    embedding2 = embedding2.unsqueeze(0)

    similarity = torch.nn.functional.cosine_similarity(embedding1, embedding2).item()
    
    return similarity >= threshold, similarity

def detect_faces(existing_embeddings, frame):
    matched_students = []  # List to store matched student IDs

    faces = detector.detect_faces(frame)


    for face in faces:
        x, y, width, height = face['box']
        cropped_face = frame[y:y + height, x:x + width]
        embedding = extract_embeddings(cropped_face)
        for student_id, data in existing_embeddings.items():
            if not data['found']:  # Check if the embedding is valid
                # Assuming you have a function to compare face embeddings
                matched = False
                if compare_faces_torch(embedding, data['frontal']) or compare_faces_torch(embedding, data['left']) or compare_faces_torch(embedding, data['right']):  # Replace with your actual comparison logic
                    matched_students.append(student_id)  # Add matched student ID to the list\

    return matched_students 