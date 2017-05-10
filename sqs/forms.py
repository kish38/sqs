from django import forms
from django.db import models

from .models import Student,School,Quiz,Question,Answer

class StudentForm(forms.ModelForm):
	class Meta:
		model = Student
		school = models.ForeignKey(School)
		password = forms.CharField(widget=forms.PasswordInput)
		widgets = {
            'password': forms.PasswordInput(),
        }
		fields = ('login_id','name','password','school','user')

class SchoolForm(forms.ModelForm):
	class Meta:
		model = School
		fields = ('sc_id','school_name','city_name')


class QuizForm(forms.ModelForm):
	class Meta:
		model = Quiz
		fields = ('title','start_date','end_date','duration')

	def process(self):
		start_date = self.cleaned_data.get("start_date")
		end_date = self.cleaned_data.get("end_date")
		duration = self.cleaned_data.get('duration')
		msg = ''
		if end_date <= start_date:
			msg = u"End date should be greater than start date."
			self._errors["end_date"] = self.error_class([msg])
		elif duration <= 0:
			msg = u"Invalid Duration"
			self._errors["duration"] = self.error_class([msg])
		return msg

class QuestionForm(forms.ModelForm):
	class Meta:
		model = Question
		exclude = ('quiz',)

class AnswerForm(forms.ModelForm):
	class Meta:
		model = Answer
		exclude = ('quiz',)

class UploadCSVForm(forms.Form):
	file = forms.FileField()

	def process_csv_file(csv):
		print (csv.name)
