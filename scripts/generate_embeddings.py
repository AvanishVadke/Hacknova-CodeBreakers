"""
Generate Face Embeddings Script
Generate and store face embeddings for all students
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import numpy as np
import pandas as pd
from cv_pipeline.face_recognition.recognizer import FaceRecognition
from backend.app.core.database import SessionLocal
from backend.app.models.student import Student

def generate_embeddings():
    """
    Generate face embeddings for all students from their photos
    """
    print("🔍 Starting face embedding generation...")
    
    # Initialize face recognizer
    fr = FaceRecognition()
    
    # Create embeddings directory
    embeddings_dir = "data/embeddings"
    os.makedirs(embeddings_dir, exist_ok=True)
    
    # Load students from database
    db = SessionLocal()
    students = db.query(Student).all()
    
    print(f"👥 Processing {len(students)} students...")
    
    for student in students:
        try:
            # Path to student photo (assumed to be in data/photos/)
            photo_path = f"data/photos/{student.moodle_id}.jpg"
            
            if not os.path.exists(photo_path):
                print(f"⚠️  Photo not found for {student.moodle_id}")
                continue
            
            # Detect faces
            faces = fr.detect_faces(photo_path)
            
            if len(faces) == 0:
                print(f"⚠️  No face detected for {student.moodle_id}")
                continue
            
            # Generate embedding for first detected face
            embedding = fr.generate_embedding(faces[0])
            
            # Save embedding
            embedding_path = os.path.join(embeddings_dir, f"{student.moodle_id}.npy")
            np.save(embedding_path, embedding)
            
            # Update database with embedding
            student.face_embedding = embedding.tolist()
            db.commit()
            
            print(f"✅ Generated embedding for {student.name} ({student.moodle_id})")
            
        except Exception as e:
            print(f"❌ Error processing {student.moodle_id}: {e}")
            continue
    
    db.close()
    print("🎉 Face embedding generation completed!")

if __name__ == "__main__":
    generate_embeddings()
