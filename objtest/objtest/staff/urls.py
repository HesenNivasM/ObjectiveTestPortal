from django.urls import path
from . import views


urlpatterns = [
    path('', views.staff_dashboard, name="staff_dashboard"),
    path('questions/', views.staff_questions, name="staff_questions"),
    path('results/', views.staff_results, name="staff_results"),
]
