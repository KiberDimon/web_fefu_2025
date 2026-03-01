from .forms import FeedbackForm
from .models import Student, Instructor, Course, Enrollment
from django.shortcuts import get_object_or_404
from .forms import EnrollmentForm
from django.db import DatabaseError
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import RegisterForm, LoginForm
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import user_passes_test
from .forms import UserEditForm, StudentEditForm
from django.db import transaction
from django.contrib import messages
from django.db.models import Count

def home_page(request):
    total_students = Student.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_instructors = Instructor.objects.filter(is_active=True).count()
    recent_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:3]

    return render(request, 'fefu_lab/homePage.html', {
        'title': 'Главная страница',
        'total_students': total_students,
        'total_courses': total_courses,
        'total_instructors': total_instructors,
        'recent_courses': recent_courses,
    })

def about_page(request):
    return render(request, 'fefu_lab/about.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # ВАЖНО: сначала указать backend, потом один раз вызвать login
            user.backend = 'fefu_lab.backends.EmailBackend'  # или 'django.contrib.auth.backends.ModelBackend'
            login(request, user)

            return redirect('student_dashboard')
    else:
        form = RegisterForm()

    return render(request, 'fefu_lab/registration/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                role = user.student_profile.role
                if role in ['TEACHER', 'ADMIN']:
                    return redirect('teacher_dashboard')
                else:
                    return redirect('student_dashboard')
            else:
                form.add_error(None, "Неверный email или пароль")
    else:
        form = LoginForm()
    return render(request, 'fefu_lab/registration/login.html', {'form': form})

def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            return render(request, 'fefu_lab/success.html', {
                'title': 'Обратная связь',
                'message': 'Спасибо за ваше сообщение! Мы свяжемся с вами(обязательно).'
            })
    else:
        form = FeedbackForm()

    return render(request, 'fefu_lab/feedback.html', {
        'form': form,
        'title': 'Обратная связь'
    })

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = student.enrollments.select_related('course')

    return render(request, 'fefu_lab/student_detail.html', {
        'student': student,
        'enrollments': enrollments,
    })

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollments = course.enrollments.select_related('student')

    return render(request, 'fefu_lab/course_detail.html', {
        'course': course,
        'enrollments': enrollments,
    })

def course_list(request):
    courses = Course.objects.filter(is_active=True).order_by('title')
    return render(request, 'fefu_lab/course_list.html', {
        'courses': courses,
        'title': 'Список курсов',
    })

def enrollment_view(request):
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            try:
                form.save()
            except DatabaseError:
                form.add_error(None, "Ошибка при сохранении записи в базу данных")
            else:
                return render(request, 'fefu_lab/success.html', {
                    'title': 'Запись на курс',
                    'message': 'Вы успешно записались на курс!'
                })
    else:
        form = EnrollmentForm()

    return render(request, 'fefu_lab/enrollment.html', {
        'form': form,
        'title': 'Запись на курс',
    })

@login_required
def profile_view(request):
    student = get_object_or_404(Student, user=request.user)
    enrollments = student.enrollments.select_related('course').all()

    return render(request, 'fefu_lab/registration/profile.html', {
        'student': student,
        'enrollments': enrollments,
        'title': 'Профиль',
    })

@login_required
def student_dashboard(request):
    return render(request, 'fefu_lab/dashboard/student_dashboard.html')

@login_required
def teacher_dashboard(request):
    return render(request, 'fefu_lab/dashboard/teacher_dashboard.html')

@login_required
def logout_view(request):
    auth_logout(request)
    return redirect('home')

def is_student(user):
    return hasattr(user, 'student_profile') and user.student_profile.role == 'STUDENT'

def is_teacher(user):
    return hasattr(user, 'student_profile') and user.student_profile.role in ['TEACHER', 'ADMIN']

@login_required
@user_passes_test(is_student)
def student_dashboard_view(request):
    student = request.user.student_profile
    enrollments = student.enrollments.select_related('course').all()
    return render(request, 'fefu_lab/dashboard/student_dashboard.html', {
        'student': student,
        'enrollments': enrollments,
        'title': 'Кабинет студента',
    })


@login_required
@user_passes_test(is_teacher)
def teacher_dashboard_view(request):
    # ищем Instructor, связанного с этим user'ом
    try:
        instructor = request.user.instructor_profile
    except Instructor.DoesNotExist:
        instructor = None

    if instructor is not None:
        courses = Course.objects.filter(instructor=instructor).annotate(
            students_count=Count('enrollments')
        )
    else:
        # если по какой-то причине связи нет — показываем пустой список
        courses = Course.objects.none()

    return render(request, 'fefu_lab/dashboard/teacher_dashboard.html', {
        'teacher': request.user.student_profile,
        'courses': courses,
        'title': 'Кабинет преподавателя',
    })

@login_required
@transaction.atomic
def profile_edit_view(request):
    student = request.user.student_profile

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        student_form = StudentEditForm(request.POST, request.FILES, instance=student)

        if user_form.is_valid() and student_form.is_valid():
            user_form.save()
            student_form.save()
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        student_form = StudentEditForm(instance=student)

    return render(request, 'fefu_lab/registration/profile_edit.html', {
        'user_form': user_form,
        'student_form': student_form,
        'title': 'Редактирование профиля'
    })

@login_required
def enroll_course_view(request, slug):
    course = get_object_or_404(Course, slug=slug)
    student = request.user.student_profile

    # проверка, что это вообще студент (а не препод/админ)
    if student.role != 'STUDENT':
        messages.error(request, "Запись на курс доступна только студентам.")
        return redirect(course.get_absolute_url())

    # проверяем, не записан ли уже
    if Enrollment.objects.filter(student=student, course=course).exists():
        messages.info(request, "Вы уже записаны на этот курс.")
    else:
        Enrollment.objects.create(student=student, course=course)
        messages.success(request, "Вы успешно записались на курс.")

    return redirect(course.get_absolute_url())

@login_required
@user_passes_test(is_teacher)
def course_students_view(request, slug):
    course = get_object_or_404(Course, slug=slug)
    enrollments = Enrollment.objects.select_related('student').filter(course=course)

    if request.method == 'POST':
        enrollment_id = request.POST.get('enrollment_id')
        grade = request.POST.get('grade')  # 'A', 'B', 'C', 'D' или ''

        enrollment = get_object_or_404(Enrollment, id=enrollment_id, course=course)
        if grade == '':
            enrollment.grade = None
        else:
            enrollment.grade = grade
        enrollment.save()

        messages.success(request, "Оценка обновлена.")
        return redirect('course_students', slug=course.slug)

    return render(request, 'fefu_lab/dashboard/course_students.html', {
        'course': course,
        'enrollments': enrollments,
        'title': f'Студенты курса {course.title}',
    })