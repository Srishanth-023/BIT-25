from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('login/',views.log_in,name='login'),
    path('',views.index,name='index'),
    path('addstudent/',views.add_student,name="addstudent")
]
