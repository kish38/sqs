from django.contrib import messages
from django.shortcuts import render,render_to_response
from django.http import HttpResponse

from .forms import StudentForm,QuizForm,QuestionForm,AnswerForm,UploadCSVForm
from .models import Student

import csv



def index(request):
	context = {}
	if 'login_id' in request.session :
		context['login_id'] = request.session['login_id']
	return render_to_response('index.html',context)

def register(request):
	if request.method == "POST":
		request.POST = request.POST.copy()
		request.POST['password'] = request.POST['password'].encode('base64')
		form = StudentForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.save()
			messages.success(
				request,'Registration Success'
				)
	else:
		form = StudentForm()
	return render(request,'register.html',{'form':form})

def login(request):
	if request.method == "POST":
		password = request.POST['password'].encode('base64')
		student_list = Student.objects.filter(login_id=request.POST['loginid'])
		if len(student_list) < 1:
			messages.success(
				request,'No User Exists with login_id '+request.POST['loginid']
				)
		elif student_list[0].password != password.strip():
			messages.success(
				request,'Invalid Credentials'
				)
		else:
			request.session['login_id'] = request.POST['loginid']

	return render(request,'login.html',{})

def logout(request):
	if 'login_id' in request.session:
		request.session.pop('login_id')
	return render(request,'index.html',{})
def admin(request):
	return render(request,'admin.html',{})

def quiz_setup(request):
	if request.method == 'POST':
		context = {}
		if request.POST['display'] == 'quiz':
			form = QuizForm(request.POST)
			if form.is_valid():
				if form.process() == '':
					quiz_p = form.save()
					context['quiz_id'] = quiz_p.id

					form = QuestionForm()
					context['quizf'] = form
					context['display'] =  'question'
	else:
		form = QuizForm(prefix='quiz')
		context = {'quizf':form,'display':'quiz'}
		'''
		quesf = QuestionForm(prefix='question')
		answf = AnswerForm(prefix='answer')
		'''
	return render(request,'quiz_setup.html',context)

def csv_upload(request):
	return render(request,'csv_upload.html',{})