from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='home'),
    path('about/', views.about_page, name='about'),
    path('student/<int:pk>/', views.student_detail, name='student_detail'),
    path('registration/register/', views.register_view, name='register'),
    path('registration/login/', views.login_view, name='login'),
    path('feedback/', views.feedback_view, name='feedback'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/enroll/', views.enroll_course_view, name='course_enroll'),
    path('course/', views.course_list, name='course_list'),
    path('enroll/', views.enrollment_view, name='enrollment'),
    path('dashboard/student/', views.student_dashboard_view, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard_view, name='teacher_dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('dashboard/teacher/course/<slug:slug>/students/', views.course_students_view, name='course_students'),
]
