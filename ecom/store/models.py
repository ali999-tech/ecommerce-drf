from django.db import models
from django.contrib.auth.models import User
import numpy as np
import os
import face_recognition

class Category(models.Model):
    name = models.CharField(max_length=100)

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    products = models.ManyToManyField(Product)

class FaceProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='faces/')
    face_encoding = models.BinaryField()  # Store face encoding as binary data

    def save(self, *args, **kwargs):
        if self.image:
            try:
                # Check if the file exists
                if not os.path.exists(self.image.path):
                    raise FileNotFoundError(f"Image file not found at {self.image.path}")

                # Load the image data from the file
                face_image_data = face_recognition.load_image_file(self.image.path)
                
                # Get face encodings
                encodings = face_recognition.face_encodings(face_image_data)
                if encodings:
                    self.face_encoding = np.array(encodings[0]).tobytes()  # Convert numpy array to bytes
                else:
                    raise ValueError("No face found in the image")
            
            except FileNotFoundError as fnf_error:
                raise fnf_error  # Reraise the file not found error
            except Exception as e:
                raise Exception(f"Error processing the image: {str(e)}")
        
        # Proceed with saving the FaceProfile object
        super(FaceProfile, self).save(*args, **kwargs)


