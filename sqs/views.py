from django.contrib import messages
from django.shortcuts import render,render_to_response
from django.http import HttpResponse

from .forms import StudentForm,QuizForm,QuestionForm,AnswerForm,UploadCSVForm
from .models import Student,Quiz,Question,Answer,StudentAnswers
from .serializers import QuizSerializer

import csv,datetime
from json import loads,dumps


def index(request):
	context = {}
	if 'login_id' in request.session :
		context['login_id'] = request.session['login_id']
	if 'logged_user' in request.session:
		context['logged_user'] = request.session['logged_user']
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
	context = {}
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
			request.session['logged_user'] = 'student'

	return render(request,'login.html',context)

def logout(request):
	if 'login_id' in request.session:
		request.session.pop('login_id')
		request.session.pop('logged_user')
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

def student_view(request):
	context = {}
	if 'login_id' in request.session:
		context = {'quizes':{}}
		student = Student.objects.get(login_id=request.session['login_id'])
		quizes = Quiz.objects.filter(end_date__gte=datetime.datetime.now())
		quizestaken = StudentAnswers.objects.filter(login_id=request.session['login_id'])
		quizestaken = {quizt.quiz_id:[str(quizt.quiz_title),str(quizt.score),quizt.user_answers] for quizt in quizestaken}
		context['quizestaken'] = quizestaken
		for i in quizes:
			if str(i.id) not in quizestaken:
				context['quizes'][i.id]=i.title
		context['schoolmates'] =[scm.name for scm in Student.objects.filter(school=student.school).exclude(id=student.id)]

	return render(request,'student.html',context)
def teacher_view(request):
	return render(request,'teacher.html',{})

def prepare_quiz(request):
	quiz_id = request.GET['quiz_id']
	quiz = Quiz.objects.get(pk=quiz_id)
	quiz_ser = QuizSerializer(quiz)
	quiz_ser = quiz_ser.data

	quiz_data = loads(dumps(quiz_ser))

	context = {'quiz_data':quiz_data}
	if(request.GET['display'] == 'quiz_details'):
		context['student_answers'] = dumps(request.GET['student_answers'].replace("u'","'"))
	return render(request,request.GET['display']+'.html',context)

def submit_quiz(request):
	if request.method == 'POST':
		answers = loads(dumps(request.POST))
		answers.pop('csrfmiddlewaretoken')
		quiz_id = answers.pop('quiz_id')
		'''
		quiz = Quiz.objects.get(pk=quiz_id)
		quiz_ser = QuizSerializer(quiz)
		quiz_data = loads(dumps(quiz_ser.data))
		'''
		score = 0


		questions = [qtn.id for qtn in Question.objects.filter(quiz=quiz_id)]
		correct_ans_mult = Answer.objects.filter(question__in=questions,correct=True).exclude(question__choice=1)
		correct_ans_essay = Answer.objects.filter(question__in=questions,correct=True).exclude(question__choice__gt=1)
		
		for c_ans in correct_ans_mult:
			if (str(c_ans.question.id) in answers) and (str(c_ans.id) == answers[str(c_ans.question.id)]):
				score += 1
		for c_ans in correct_ans_essay:
			print c_ans.answer_text,answers[str(c_ans.question.id)]
			if (c_ans.answer_text == answers[str(c_ans.question.id)]):
				score += 1
		
		StudentAnswers.objects.create(quiz_id=quiz_id,quiz_title=Quiz.objects.get(pk=quiz_id).title,login_id=request.session['login_id'],user_answers=answers,score=score)

		return HttpResponse(score)