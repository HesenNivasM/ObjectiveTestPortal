from django.urls import path
from . import views


urlpatterns = [
    path('', views.student_dashboard, name="student_dashboard"),
    path('test/', views.student_test, name="student_test"),

]
