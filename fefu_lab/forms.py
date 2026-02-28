from django import forms
from django.core.exceptions import ValidationError
from .models import Student, Enrollment
from datetime import datetime

class LoginForm(forms.Form):
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
class FeedbackForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    subject = forms.CharField(
        max_length=150,
        label='Тема сообщения',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    message = forms.CharField(
        label='Сообщение',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
    )

    def clean_name(self):
        name = self.cleaned_data['name']
        if len(name.strip()) < 2:
            raise ValidationError("Имя должно содержать минимум 2 символа")
        return name.strip()

    def clean_message(self):
        message = self.cleaned_data.get('message', '')
        text = message.strip()
        if len(text) < 10:
            raise ValidationError("Сообщение должно содержать минимум 10 символов")
        return text

class StudentRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    birth_date = forms.DateField(
        required=False,
        label='Дата рождения',
        input_formats=['%d.%m.%Y', '%Y-%m-%d'],  # поддерживаем оба формата
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'дд.мм.гггг'
        })
    )

    class Meta:
        model = Student
        fields = ('first_name', 'last_name', 'email', 'birth_date', 'faculty', 'password')

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if Student.objects.filter(email=email).exists():
            raise ValidationError("Студент с таким email уже существует")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        pwd2 = cleaned_data.get('password_confirm')
        if pwd and pwd2 and pwd != pwd2:
            raise ValidationError("Пароли не совпадают")
        return cleaned_data

    def clean_birth_date(self):
        value = self.cleaned_data.get('birth_date')

        # если поле пустое — просто вернуть (оно у модели nullable)
        if not value:
            return value

        # если уже пришёл date-объект (браузер дал yyyy-mm-dd) — тоже ок
        if isinstance(value, datetime):
            return value.date()

        # если строка вида dd.mm.yyyy — разбираем вручную
        if isinstance(value, str):
            try:
                return datetime.strptime(value.strip(), "%d.%m.%Y").date()
            except ValueError:
                raise ValidationError("Дата должна быть в формате ДД.ММ.ГГГГ")

        return value


class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('student', 'course')