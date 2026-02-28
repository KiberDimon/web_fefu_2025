from django.contrib import admin
from .models import Student, Instructor, Course, Enrollment


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'faculty', 'is_active']
    list_filter = ['is_active', 'faculty']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'specialization', 'is_active']
    list_filter = ['is_active', 'specialization']
    search_fields = ['first_name', 'last_name', 'email']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'duration', 'level', 'is_active']
    list_filter = ['is_active', 'level', 'instructor']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}  # автогенерация slug


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'created_at']
    list_filter = ['status', 'course']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']

