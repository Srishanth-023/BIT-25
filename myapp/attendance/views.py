from django.shortcuts import render,redirect
from django.urls import reverse,reverse_lazy
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required
from . forms import LoginForm,StudentForm,StudentImageForm
from django.contrib.auth import authenticate
from .models import Class
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
        image_form = StudentImageForm(request.FILES)

        if student_form.is_valid():

            student = student_form.save(commit=False)
            cls = Class.objects.get(incharge = request.user.id)
            print("Here",cls)
            student.assigned_class = cls
            student.save()
        
        if image_form.is_valid():
            image = image_form.cleaned_data['image']
            


    return render(request,'attendance/addstudent.html',{'title':'Add student'})