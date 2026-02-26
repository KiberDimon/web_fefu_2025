
from django.http import HttpResponse, Http404
from django.views import View

def home_page(request):
    return HttpResponse("Добро пожаловать на главную страницу!")

def about_page(request):
    return HttpResponse("Страница о нас")

class StudentView(View):
    def get(self, request, student_id):
        if student_id > 100:
            raise Http404("Студент не найден")
        return HttpResponse(f"Профиль студента с ID: {student_id}")
