from django.shortcuts import render
from .forms import LoginForm
from .forms import FeedbackForm
from .models import Student, Instructor, Course, Enrollment
from django.shortcuts import get_object_or_404
from .forms import StudentRegistrationForm
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
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            # пароль уже в cleaned_data['password'], просто сохраняем студента
            student = form.save()
            return render(request, 'fefu_lab/success.html', {
                'title': 'Регистрация',
                'message': 'Регистрация прошла успешно! Студент добавлен в систему.'
            })
    else:
        form = StudentRegistrationForm()

    return render(request, 'fefu_lab/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()
            password = form.cleaned_data['password']

            student = Student.objects.filter(email=email, password=password).first()

            if student is not None:
                # сохраняем id в сессии
                request.session['student_id'] = student.pk

                return render(request, 'fefu_lab/success.html', {
                    'title': 'Вход в систему',
                    'message': f'Вход выполнен успешно! Добро пожаловать, {student.full_name}.'
                })
            else:
                form.add_error(None, "Неверный email или пароль")
    else:
        form = LoginForm()

    return render(request, 'fefu_lab/login.html', {
        'form': form,
        'title': 'Вход в систему'
    })
def feedback_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # здесь можно было бы сохранить в БД или отправить email
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