from rest_framework import viewsets, permissions, filters, status
from .models import Product, Category, Order, FaceProfile
from .serializers import ProductSerializer, CategorySerializer, OrderSerializer, UserSerializer, FaceProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.core.files.base import ContentFile
import base64
from django.contrib import messages
import face_recognition
import numpy as np
from django.core.files.storage import default_storage
import os
from rest_framework.permissions import AllowAny

def compare_faces(known_face_encoding, uploaded_face_encoding, threshold=0.6):
    matches = face_recognition.compare_faces([known_face_encoding], uploaded_face_encoding)
    distances = face_recognition.face_distance([known_face_encoding], uploaded_face_encoding)
    match = False

    # If faces match and distance is below the threshold
    if matches[0] and distances[0] <= threshold:
        match = True
    return match, distances[0]  # Return whether there's a match and the distance

# Login view
def login_view(request):
    if request.method == 'POST':
        # Get the username and face image from the form
        username = request.POST.get('username')
        uploaded_face_image = request.FILES.get('face')  # Assuming 'face' is the name of the input field

        if username and uploaded_face_image:
            try:
                # Get the user based on the username
                user = User.objects.get(username=username)

                # Retrieve the known face encoding from the user's profile (assuming it's saved in a UserProfile model)
                known_face_encoding = user.profile.face_encoding  # Make sure user has a 'profile' with 'face_encoding'

                # Convert the uploaded face image to face encoding
                uploaded_face_image_data = uploaded_face_image.read()
                uploaded_face_encoding = face_recognition.face_encodings(face_recognition.load_image_file(uploaded_face_image_data))[0]

                # Compare the known face with the uploaded face using a threshold
                match, distance = compare_faces(known_face_encoding, uploaded_face_encoding, threshold=0.6)

                if match:
                    # If faces match, authenticate and log in the user
                    user = authenticate(request, username=username)
                    if user is not None:
                        login(request, user)
                        return redirect('home')  # Redirect to home page after successful login
                    else:
                        messages.error(request, 'Authentication failed')
                        return redirect('login')
                else:
                    # If faces do not match
                    messages.error(request, f'Face mismatch! Distance: {distance}')
                    return redirect('login')

            except User.DoesNotExist:
                messages.error(request, 'User not found')
                return redirect('login')
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")
                return redirect('login')

    return render(request, 'login.html') 

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'description']

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class HomePageView(TemplateView):
    template_name = 'index.html'
    
def compare_faces(known_face_encoding, uploaded_face_encoding, threshold=0.6):
    matches = face_recognition.compare_faces([known_face_encoding], uploaded_face_encoding)
    distances = face_recognition.face_distance([known_face_encoding], uploaded_face_encoding)

    if matches[0] and distances[0] <= threshold:
        return True, distances[0]  # Faces match
    else:
        return False, distances[0]  # Faces don't match


# Register view
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        face_img = request.FILES['face']

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken. Please choose another one."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if passwords match
        if password != password2:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        # Create new user
        user = User.objects.create_user(username=username, password=password)

        # Save the face image
        uploaded_image = face_recognition.load_image_file(face_img)
        face_encoding = face_recognition.face_encodings(uploaded_image)[0]

        # Save face encoding as a binary field
        face_encoding_bytes = face_encoding.tobytes()

        # Create the FaceProfile and save it with face encoding and image
        profile = FaceProfile.objects.create(user=user, image=face_img, face_encoding=face_encoding_bytes)

        return redirect('home')



# Login view
class LoginFaceView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'login.html')

    def post(self, request):
        username = request.POST.get('username')
        face_img = request.FILES.get('face')

        if not username or not face_img:
            return render(request, 'login.html', {"error": "Username and face image are required."})

        user = User.objects.filter(username=username).first()
        if not user:
            return render(request, 'login.html', {"error": "User not found."})

        try:
            profile = FaceProfile.objects.get(user=user)
        except FaceProfile.DoesNotExist:
            return render(request, 'login.html', {"error": "No face profile found for this user."})

        # Load the known face encoding from the profile image
        known_face_encoding = np.frombuffer(profile.face_encoding, dtype=np.float64)

        # Load the uploaded face image for comparison
        uploaded_img = face_recognition.load_image_file(face_img)
        uploaded_encodings = face_recognition.face_encodings(uploaded_img)

        if not uploaded_encodings:
            return render(request, 'login.html', {"error": "No face found in uploaded image."})

        uploaded_face_encoding = uploaded_encodings[0]

        # Compare the faces
        match_result, distance = compare_faces(known_face_encoding, uploaded_face_encoding)

        if match_result:
            login(request, user)
            return redirect('home')  # Redirect to home page after successful login
        else:
            # If faces don't match, show the error message
            return render(request, 'login.html', {"error": f"Face does not match. Distance: {distance:.2f}"})
