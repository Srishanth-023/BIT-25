from django.shortcuts import render,redirect
from django.urls import reverse,reverse_lazy
from django.http.response import HttpResponse
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from . forms import LoginForm,StudentForm,StudentImageForm,NewClassForm
from django.contrib.auth import authenticate
from .models import Attendance, Class,Student,StudentImage
from django.contrib.auth.models import User
import random
import io
from PIL import Image, ImageEnhance, ImageFilter
from django.core.files.base import ContentFile
from datetime import date
from django.contrib import messages
from datetime import datetime
from django.utils.timezone import localtime
import cv2
import face_recognition
import numpy as np
import mediapipe as mp
import torch
from torchvision import transforms
from PIL import Image
from django.utils.timezone import now
# Create your views here.


def log_in(request):
    
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username,password=password)

            if username and password and user is not None:
                login(request,user)
                return redirect(reverse('attendance:index'))
    return render(request,'attendance/login.html',{'title':'Login','form':form})
    

@login_required(login_url=reverse_lazy('attendance:login'))
def index(request):
    
    return render(request,'attendance/index.html',{'title':'Index'})

@login_required(login_url=reverse_lazy('attendance:login'))
def add_student(request):
    student_form = StudentForm()
    image_form = StudentImageForm()
    if request.method == 'POST':
        student_form = StudentForm(request.POST)
        image_form = StudentImageForm(request.POST, request.FILES)

        if student_form.is_valid():
            student = student_form.save(commit=False)
            cls = Class.objects.get(incharge=request.user.id)
            
            student.assigned_class = cls
            student.save()

            if image_form.is_valid():
                image = image_form.cleaned_data['image']
                original_image = Image.open(image).convert("RGB")

                for i in range(10):
                    transformed_image = original_image.copy()
                    transformations = [
                        lambda img: img.rotate(random.randint(-180, 180)),
                        lambda img: ImageEnhance.Brightness(img).enhance(random.uniform(0.05, 3.0)),
                        lambda img: ImageEnhance.Contrast(img).enhance(random.uniform(0.1, 4.0)),
                        lambda img: ImageEnhance.Sharpness(img).enhance(random.uniform(0.0, 10.0)),
                        lambda img: img.filter(ImageFilter.GaussianBlur(radius=random.uniform(3, 8))),
                        lambda img: img.convert("L").convert("RGB"),
                        lambda img: img.transpose(Image.FLIP_LEFT_RIGHT),
                        lambda img: img.filter(ImageFilter.FIND_EDGES),
                        lambda img: img.filter(ImageFilter.EMBOSS),
                    ]

                    random.shuffle(transformations)
                    num_transforms = random.randint(2, 5)

                    for transform in transformations[:num_transforms]:
                        transformed_image = transform(transformed_image)

                    img_io = io.BytesIO()
                    transformed_image.save(img_io, format="JPEG")
                    img_io.seek(0)

                    StudentImage.objects.create(student=student, image=ContentFile(img_io.getvalue(), name=f"{student.name}_{i+1}.jpg"))

                messages.success(request,"Student added successfully.")
                return redirect(reverse("attendance:index"))

    return render(request, 'attendance/addstudent.html', {'title': 'Add student', 'student_form': student_form, 'image_form': image_form})


@login_required(login_url=reverse_lazy('attendance:login'))
def new_class(request):
    if request.user.is_superuser:
        incharges = User.objects.exclude(username=request.user)
        form = NewClassForm()
        if request.method == 'POST':
            form = NewClassForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(request,'New class has been added')
        return render(request,"attendance/addclass.html",{'incharges':incharges,'title':'New Class','form':form})
    else:
        messages.warning(request,"You don't have permission to do this action.")
        return redirect(reverse("attendance:index"))
    

@login_required(login_url=reverse_lazy('attendance:login'))
def take_attendance(request):
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(
        static_image_mode=False,
        max_num_faces=100,
        refine_landmarks=True,
        min_detection_confidence=0.8,
        min_tracking_confidence=0.8
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_small", trust_repo=True).to(device).eval()

    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Resize((384, 384)),
        transforms.Normalize(mean=[0.5], std=[0.5])
    ])
    
    students = Student.objects.filter(assigned_class__incharge=request.user)
    student_images = StudentImage.objects.filter(student__in=students)
    
    known_face_encodings = []
    known_face_names = []
    # count = 1
    for student_image in student_images:
        
        try:
            # count+=1
            # print(count)
            image = face_recognition.load_image_file(student_image.image)
            encoding = face_recognition.face_encodings(image, model="hog", num_jitters=10)
            
            
            if encoding:
                known_face_encodings.append(encoding[0])
                known_face_names.append(student_image.student.name)
        except Exception as e:
            print("ERROR:",e)

    if not known_face_encodings:
        return HttpResponse("No student face data found. Please add student images.", status=400)
    print("Get ready...")
    cap = cv2.VideoCapture(0)
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        if frame_count % 3 != 0:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame, model="hog")
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations, num_jitters=2)
        
        results = face_mesh.process(rgb_frame) if len(face_locations) > 0 else None
        
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances) if len(face_distances) > 0 else -1
            name = "Unmatched"

            if best_match_index != -1 and matches[best_match_index] and face_distances[best_match_index] < 0.5:
                name = known_face_names[best_match_index]
            
            student = Student.objects.filter(name=name).first()
            if student:
                current_time = localtime().time()

                attendance, created = Attendance.objects.get_or_create(student=student, date=now().date())
                if datetime.strptime("08:45", "%H:%M").time() <= current_time <= datetime.strptime("09:40", "%H:%M").time():
                    attendance.period_1 = True
                elif datetime.strptime("09:40", "%H:%M").time() <= current_time <= datetime.strptime("10:35", "%H:%M").time():
                    attendance.period_2 = True
                elif datetime.strptime("10:50", "%H:%M").time() <= current_time <= datetime.strptime("11:40", "%H:%M").time():
                    attendance.period_3 = True
                elif datetime.strptime("11:40", "%H:%M").time() <= current_time <= datetime.strptime("12:25", "%H:%M").time():
                    attendance.period_4 = True
                elif datetime.strptime("13:25", "%H:%M").time() <= current_time <= datetime.strptime("14:10", "%H:%M").time():
                    attendance.period_5 = True
                elif datetime.strptime("14:10", "%H:%M").time() <= current_time <= datetime.strptime("15:10", "%H:%M").time():
                    attendance.period_6 = True
                elif datetime.strptime("15:10", "%H:%M").time() <= current_time <= datetime.strptime("15:50", "%H:%M").time():
                    attendance.period_7 = True
                elif datetime.strptime("15:50", "%H:%M").time() <= current_time <= datetime.strptime("16:30", "%H:%M").time():
                    attendance.period_8 = True

                attendance.save()
                print(f"Attendance marked for {name}: Present")
            else:
                print(f"Student {name} not found in database. Skipping attendance update.")
            
            color = (0, 255, 0) if name != "Unmatched" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, name, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)

        cv2.imshow("Face Recognition Attendance System", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    # messages.success(request,"Attendance has been taken successfully.")
    return redirect(reverse("attendance:showattendance"))

@login_required(login_url=reverse_lazy('attendance:login'))
def show_attendance(request):
    students = Student.objects.filter(assigned_class__incharge=request.user)
    today = date.today()
    
    for student in students:
        student.attendance = Attendance.objects.filter(student=student, date=today).first()
        print(student.attendance)
        classname = student.assigned_class
     
    return render(request,'attendance/showattendance.html',{"students":students,'today':today,'classname':classname})

def logout_view(request):
    logout(request)
    return redirect("attendance:index")