from django.db import models
from django.contrib.auth.models import User  

# Create your models here.

class Class(models.Model):
    name = models.CharField(max_length=50, unique=True) 
    incharge = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,unique=True)#

    def __str__(self):
        return f"{self.name} (Incharge: {self.incharge.username if self.incharge else 'None'})"

class Student(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    parent_phone = models.CharField(max_length=15, null=True, blank=True)
    assigned_class = models.ForeignKey(Class, on_delete=models.CASCADE)  
    created_at = models.DateTimeField(auto_now_add=True)
    roll_no = models.CharField(unique=True,max_length=8,null=False)
    def __str__(self):
        return f"{self.name} - {self.assigned_class.name}"


class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()  

    period_1 = models.BooleanField(default=False)  
    period_2 = models.BooleanField(default=False)
    period_3 = models.BooleanField(default=False)
    period_4 = models.BooleanField(default=False)
    period_5 = models.BooleanField(default=False)
    period_6 = models.BooleanField(default=False)
    period_7 = models.BooleanField(default=False)
    period_8 = models.BooleanField(default=False)
    class Meta:
        unique_together = ('student', 'date') 

    def __str__(self):
        return f"{self.student.name} - {self.date}"


class StudentImage(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="student_images/")  
    

    class Meta:
        unique_together = ('student', 'image')

    def __str__(self):
        return f"Image of {self.student.name}"
    
    @property
    def formeted_image(self):

        if self.image.__str__().startswith(('http://','https://')):
            url = self.image
        else:
            url = self.image.url
            
        return url
