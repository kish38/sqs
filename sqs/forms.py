from django import forms
from django.db import models

from .models import Student,School

class StudentForm(forms.ModelForm):
	class Meta:
		model = Student
		school = models.ForeignKey(School)
		password = forms.CharField(widget=forms.PasswordInput)
		widgets = {
            'password': forms.PasswordInput(),
        }
		fields = ('login_id','name','password','school')