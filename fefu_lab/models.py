from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Instructor(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        verbose_name='Пользователь',
        null=True,
        blank=True,  # пока можно оставить, чтобы не ломать старые данные
    )
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Email')
    specialization = models.CharField(max_length=150, verbose_name='Специализация', blank=True)
    degree = models.CharField(max_length=150, verbose_name='Учёная степень', blank=True)
    is_active = models.BooleanField(default=True, verbose_name='Активен')

    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Student(models.Model):
    # связь с встроенным пользователем
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='Пользователь',
        null=True,
        blank=True       # на переходный период можно оставить blank, потом сделаем обязательным
    )

    FACULTY_CHOICES = [
        ('CS', 'Кибербезопасность'),
        ('SE', 'Программная инженерия'),
        ('IT', 'Информационные технологии'),
        ('DS', 'Наука о данных'),
        ('WEB', 'Веб-технологии'),
    ]

    ROLE_CHOICES = [
        ('STUDENT', 'Студент'),
        ('TEACHER', 'Преподаватель'),
        ('ADMIN', 'Администратор'),
    ]

    # старые поля (можем постепенно переносить в User, но пока оставим для совместимости)
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Email')

    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения'
    )
    faculty = models.CharField(
        max_length=3,
        choices=FACULTY_CHOICES,
        default='CS',
        verbose_name='Факультет'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    # новые поля из ТЗ
    avatar = models.ImageField(
        upload_to='avatars/',
        null=True,
        blank=True,
        verbose_name='Аватар'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='STUDENT',
        verbose_name='Роль'
    )

    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['last_name', 'first_name']
        db_table = 'students'

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

    def get_absolute_url(self):
        return reverse('student_detail', kwargs={'pk': self.pk})

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_faculty_display_name(self):
        return dict(self.FACULTY_CHOICES).get(self.faculty, 'Неизвестно')


class Course(models.Model):
    LEVEL_CHOICES = [
        ('BEGINNER', 'Начальный'),
        ('INTERMEDIATE', 'Средний'),
        ('ADVANCED', 'Продвинутый'),
    ]

    title = models.CharField(max_length=200, unique=True, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='Слаг')
    description = models.TextField(verbose_name='Описание')
    duration = models.PositiveIntegerField(verbose_name='Продолжительность (часы)')
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.PROTECT,
        related_name='courses',
        verbose_name='Преподаватель'
    )
    level = models.CharField(
        max_length=12,
        choices=LEVEL_CHOICES,
        default='BEGINNER',
        verbose_name='Уровень'
    )
    max_students = models.PositiveIntegerField(default=30, verbose_name='Максимум студентов')
    price = models.PositiveIntegerField(default=0, verbose_name='Цена')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})


class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Активен'),
        ('FINISHED', 'Завершен'),
    ]

    GRADE_CHOICES = [
        ('A', 'Отлично'),
        ('B', 'Хорошо'),
        ('C', 'Удовлетворительно'),
        ('D', 'Неудовлетворительно'),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Студент'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Курс'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата записи')
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        verbose_name='Статус'
    )
    grade = models.CharField(
        max_length=1,
        choices=GRADE_CHOICES,
        blank=True,
        null=True,
        verbose_name='Оценка'
    )

    class Meta:
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student} → {self.course} ({self.status})"

