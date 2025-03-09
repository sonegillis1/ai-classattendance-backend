import cv2
import torch
from torchvision import models, transforms
from torch import nn
import numpy as np
from sklearn.preprocessing import Normalizer

# Load a pre-trained ResNet model for face recognition (you can use other models like FaceNet)
model = models.resnet18(pretrained=True)  # Use a lighter model or a custom one for face recognition
model.eval()

# Define a transformation to apply to the images
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])

# This function would capture face embeddings and save them
def extract_embeddings(face_image):
    # Preprocess the face image
    face_tensor = transform(face_image).unsqueeze(0)
    
    # Get the embedding from the model
    with torch.no_grad():
        embedding = model(face_tensor)
    
    # Normalize the embeddings for consistency
    normalizer = Normalizer()
    normalized_embedding = normalizer.fit_transform(embedding.numpy())
    
    return normalized_embedding
