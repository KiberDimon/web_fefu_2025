from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('about/', views.about_page, name='about'),
    path('student/<int:pk>/', views.student_detail, name='student_detail'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/', views.course_list, name='course_list'),
]
