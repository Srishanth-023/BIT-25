from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django import forms

from .models import Student,Class

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
    email = forms.EmailField( required=True)
    parent_phone = forms.IntegerField(required=True)
    roll_no = forms.CharField(required=True)
    class Meta:
        model = Student
        fields = ['name', 'email', 'parent_phone','roll_no']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Parent Phone'}),
        }
    
    # def clean(self):
    #     cleaned_data =  super().clean()
    #     roll_no = cleaned_data.get('roll_no')
    #     if Student.objects.filter(roll_no=roll_no).exists():

    #         raise forms.ValidationError("The roll no already exist.")


class StudentImageForm(forms.Form):
    image = forms.ImageField(required=True,)


class NewClassForm(forms.ModelForm):

    name = forms.CharField(max_length=15,required=True)
    incharge = forms.ModelChoiceField(queryset=User.objects.all(),required=True)

    class Meta:
        model = Class
        fields = ['name','incharge']