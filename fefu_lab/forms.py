from django import forms
from .models import Student, Enrollment
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserChangeForm


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

class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    password_confirm = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return email

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get('password')
        pwd2 = cleaned_data.get('password_confirm')

        if pwd and pwd2 and pwd != pwd2:
            raise ValidationError("Пароли не совпадают")

        if pwd:
            validate_password(pwd)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data['email'].strip().lower()
        user.username = email
        user.email = email
        user.set_password(self.cleaned_data['password'])

        if commit:
            user.save()
            Student.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                role='STUDENT'
            )
        return user



class EnrollmentForm(forms.ModelForm):
    class Meta:
        model = Enrollment
        fields = ('student', 'course')

class UserEditForm(UserChangeForm):
    password = None  # чтобы не показывать поле пароля

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Пользователь с таким email уже существует")
        return email

class StudentEditForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ('phone', 'bio', 'avatar', 'faculty')
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'faculty': forms.Select(attrs={'class': 'form-control'}),
        }