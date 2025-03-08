from django.urls import path
from . import views

app_name = 'attendance'

urlpatterns = [
    path('login/',views.log_in,name='login'),
    path('',views.index,name='index'),
    path('addstudent/',views.add_student,name="addstudent"),
    path('addclass/',views.new_class,name="addclass"),
    path('takeattendance/',views.take_attendance,name="takeattendance"),
    path('attendance/',views.show_attendance,name="showattendance"),
    path("logout/",views.logout_view,name="logout"),
]
