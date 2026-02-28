from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('about/', views.about_page, name='about'),
    path('student/<int:student_id>/', views.student_profile, name='student'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('feedback/', views.feedback_view, name='feedback'),
]
