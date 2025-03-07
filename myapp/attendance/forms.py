from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django import forms

from .models import Student

class LoginForm(forms.Form):

    username = forms.CharField( max_length=20, required=True)
    password = forms.CharField(min_length=8,max_length=20,required=True)

    def clean(self):
        cleaned_data = super().clean()

        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if password and username:

            user = authenticate(username=username,password=password)

            if user is None:
                raise forms.ValidationError("Invalid username and password.")
            


class StudentForm(forms.ModelForm):
    name = forms.CharField(required=True)
    email = forms.EmailField( required=False)
    parent_phone = forms.IntegerField(required=True)
    class Meta:
        model = Student
        fields = ['name', 'email', 'parent_phone',]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Parent Phone'}),
        }

class StudentImageForm(forms.Form):
    image = forms.ImageField(required=True,)