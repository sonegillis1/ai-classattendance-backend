import cv2
from mtcnn import MTCNN
import numpy as np

detector = MTCNN()

# Define the 3D model points for facial landmarks
FACE_3D_MODEL = np.array([
    (0.0, 0.0, 0.0),           # Nose tip
    (-30.0, -35.0, -10.0),     # Left eye left corner
    (30.0, -35.0, -10.0),      # Right eye right corner
    (-25.0, 40.0, -20.0),      # Left mouth corner
    (25.0, 40.0, -20.0),       # Right mouth corner
    (0.0, 65.0, -10.0)         # Chin
], dtype=np.float32)

def rotation_matrix_to_euler_angles(R):
    """
    Converts a rotation matrix to Euler angles (yaw, pitch, roll).
    Returns angles in degrees.
    """
    sy = np.sqrt(R[0, 0]**2 + R[1, 0]**2)

    singular = sy < 1e-6  # Check for singularity

    if not singular:
        yaw = np.arctan2(R[2, 0], R[2, 2])
        pitch = np.arctan2(-R[2, 1], sy)
        roll = np.arctan2(R[1, 0], R[0, 0])
    else:
        yaw = np.arctan2(-R[1, 2], R[1, 1])
        pitch = np.arctan2(-R[2, 1], sy)
        roll = 0

    return np.degrees(yaw), np.degrees(pitch), np.degrees(roll)

def get_yaw_angle(keypoints, image_shape):
    """
    Estimates the yaw angle using 3D pose reconstruction.
    
    Parameters:
    - keypoints: Facial landmarks detected by MTCNN
    - image_shape: Tuple (height, width) of the image
    
    Returns:
    - float: Yaw angle in degrees
    """
    height, width = image_shape[:2]

    # Map 2D landmarks from detected face to 3D model
    FACE_2D_LANDMARKS = np.array([
        keypoints['nose'],
        keypoints['left_eye'],
        keypoints['right_eye'],
        keypoints['mouth_left'],
        keypoints['mouth_right'],
        ((keypoints['left_eye'][0] + keypoints['right_eye'][0]) // 2, keypoints['left_eye'][1] + 50)  # Approximate chin
    ], dtype=np.float32)

    # Camera Intrinsics
    focal_length = width * 1.2  # Approximation for focal length
    camera_matrix = np.array([
        [focal_length, 0, width / 2],
        [0, focal_length, height / 2],
        [0, 0, 1]
    ], dtype=np.float32)

    # No lens distortion assumed
    dist_coeffs = np.zeros((4, 1), dtype=np.float32)

    # Solve PnP to estimate rotation and translation
    success, rotation_vector, translation_vector = cv2.solvePnP(
        FACE_3D_MODEL, FACE_2D_LANDMARKS, camera_matrix, dist_coeffs
    )

    if not success:
        return None

    # Convert rotation vector to rotation matrix
    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)

    # Extract yaw, pitch, and roll
    yaw, pitch, roll = rotation_matrix_to_euler_angles(rotation_matrix)
    
    return yaw


def detect_face_and_orientation(image):
    """
    Detects a face in the given image and determines its orientation.

    Parameters:
    image (numpy.ndarray): The input image in which to detect the face.

    Returns:
    tuple: A tuple containing (a, b, c) where:
           a: 1 if a face is detected, 0 if no face, -1 if more than one face.
           b: 1 for right side face, 0 for frontal face, -1 for left side face, None if no face.
           c: Cropped image of the detected face, or None if no face.

    Process:
    1. Detects faces and facial landmarks using MTCNN.
    2. If exactly one face is detected, it extracts the keypoints for the left and right eyes.
    3. Computes the yaw angle based on the positions of the eyes.
    4. Classifies the face orientation as 'Frontal Face' or 'Side Face' based on the yaw angle.
    5. Displays the orientation on the image using OpenCV.

    Note:
    - The function assumes that the input image is in the correct format for MTCNN.
    - The orientation is displayed on the image, which is shown in a window.
    """
    # Detect faces and facial landmarks
    faces = detector.detect_faces(image)
    if len(faces) == 0:
        return (0, None, None)  # No face detected
    elif len(faces) > 1:
        return (-1, None, None)  # More than one face detected
    else:
        # Extract the facial landmarks
        keypoints = faces[0]['keypoints']

        yaw = get_yaw_angle(keypoints, image.shape)
        print('####### yaw is ', yaw)
        if abs(yaw) > 10:
            if (yaw > 0): face_orientation = -1 # Left side face
            else: face_orientation = 1 # Right side face
        else:
            face_orientation = 0  # Frontal face

        # Crop the face from the image
        x, y, width, height = faces[0]['box']
        cropped_face = image[y:y + height, x:x + width]

        return (1, face_orientation, cropped_face)  # Face detected