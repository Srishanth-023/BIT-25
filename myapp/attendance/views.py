from django.shortcuts import render,redirect
from django.urls import reverse,reverse_lazy
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from . forms import LoginForm,StudentForm,StudentImageForm
from django.contrib.auth import authenticate
from .models import Class,Student,StudentImage
import os
import random
import io
from PIL import Image, ImageEnhance, ImageFilter
from django.core.files.base import ContentFile
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
        image_form = StudentImageForm(request.POST,request.FILES)

        if student_form.is_valid():

            student = student_form.save(commit=False)
            cls = Class.objects.get(incharge = request.user.id)
            print("Here",cls)
            student.assigned_class = cls
            student.save()
        
            if image_form.is_valid():
                image = image_form.cleaned_data['image']
                original_image = Image.open(image).convert("RGB")

                for i in range(100):
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

                    StudentImage.objects.create(
                        student=student,
                        image=ContentFile(img_io.getvalue(), name=f"{student.name}_{i+1}.jpg")
                    )

                print(f"Saved 100 distorted images for {student.name}")



    return render(request,'attendance/addstudent.html',{'title':'Add student'}) 