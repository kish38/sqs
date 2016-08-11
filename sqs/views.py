from django.contrib import messages
from django.shortcuts import render,render_to_response
from django.http import HttpResponse

from .forms import StudentForm,QuizForm,QuestionForm,AnswerForm,UploadCSVForm
from .models import Student,Question,Answer

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
		form = QuizForm(request.POST)
		context = {'quizf':form}
		if form.is_valid():
			if form.process() == '':
				quiz_p = form.save()
				context['quiz_id'] = quiz_p.id
	else:
		form = QuizForm(prefix='quiz')
		context = {'quizf':form}
	return render(request,'quiz_setup.html',context)

def csv_upload(request):
	context = {'file_required':1}
	if request.method == 'POST':
		context['file_required'] = 0
		csv_file = request.FILES['csv_file']
		file_path = 'C:\Users\kishorekumar\Desktop\sqs\static\\'+csv_file.name
		try:
			location = open(file_path,'wb+')
		except Exception,e:
			print e
		for chunk in csv_file.chunks():
			location.write(chunk)
		location.close()
		try:
			process_csv(file_path,request.POST['quiz_id'])
		except Exception,e:
			print e
	return render(request,'csv_upload.html',context)


def process_csv(csv_file,quiz_id):
	csvfile = open(csv_file)
	contents = csvfile.readlines()
	pos = 0
	quizname = contents[pos]

	while(pos<len(contents)-1):
		pos += 1
		if contents[pos].strip() == '':
			break
		qtn = Question.objects.create(quiz_id=quiz_id,question_text=contents[pos],choice=contents[pos+1])
		pos += 1
		ans_c = int(contents[pos+int(contents[pos].strip())+1])
		for i in range(int(contents[pos])):
			if i+1 == ans_c:
				ans = Answer.objects.create(question=qtn,answer_text=contents[pos+1].strip(),correct=True)
			else:
				ans = Answer.objects.create(question=qtn,answer_text=contents[pos+1].strip(),correct=False)
			pos += 1
		pos += 1

	print 'check it'
