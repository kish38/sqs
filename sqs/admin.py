from django.contrib import admin

from .models import School,Student,Quiz,Question,Answer,StudentAnswers

admin.site.register(School)
admin.site.register(Student)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(StudentAnswers)
