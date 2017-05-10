from django.contrib import messages
from django.shortcuts import render,render_to_response
from django.http import HttpResponse

from .forms import StudentForm,QuizForm,QuestionForm,AnswerForm,UploadCSVForm,SchoolForm
from .models import School,Student,Quiz,Question,Answer,StudentAnswers
from .serializers import QuizSerializer,SchoolSerializer

import csv,datetime,os
from json import loads,dumps


def index(request):
	context = {}
	if 'login_id' in request.session :
		context['login_id'] = request.session['login_id']
	if 'logged_user' in request.session:
		context['logged_user'] = request.session['logged_user']
	lbd = get_leaderboard()
	context['leaders'] = lbd['leaders']
	context['school_leaders'] = lbd['school_leaders']
	return render_to_response('index.html',context)

def register(request):
	if request.method == "POST":
		request.POST = request.POST.copy()
		request.POST['password'] = request.POST['password'].encode('base64').strip()
		form = StudentForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.save()
			messages.success(
				request,'Registration Success'
				)
	else:
		form = StudentForm(initial={'max_number': '3'})
	return render(request,'register.html',{'form':form})

def login(request):
	context = {}
	if request.method == "POST":
		password = request.POST['password'].encode('base64')
		student_list = Student.objects.filter(login_id=request.POST['loginid'],user=request.POST['user'])
		if len(student_list) < 1:
			messages.error(
				request,'No '+request.POST['user']+' Exists with login_id '+request.POST['loginid']
				)
		elif student_list[0].password != password.strip():
			messages.error(
				request,'Invalid Credentials'
				)
		else:
			request.session['login_id'] = request.POST['loginid']
			request.session['logged_user'] = request.POST['user']
			print( request.POST['user'])
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
		form = QuizForm()
		context = {'quizf':form}
	return render(request,'quiz_setup.html',context)

def csv_upload(request):
	context = {'file_required':1}
	if request.method == 'POST':
		context['file_required'] = 0
		csv_file = request.FILES['csv_file']
		BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
		file_path = os.path.join(BASE_DIR,csv_file.name)
		try:
			location = open(file_path,'wb+')
		except Exception as e:
			print (e)
		for chunk in csv_file.chunks():
			location.write(chunk)
		location.close()
		try:
			process_csv(file_path,request.POST['quiz_id'])
			qser = QuizSerializer(Quiz.objects.get(pk=request.POST['quiz_id']))
			context['added_quiz'] = qser.data
		except Exception as e:
			print (e)
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
		context['schoolmates'] =[scm for scm in Student.objects.filter(school=student.school,user=student.user).exclude(id=student.id)]
		context['student_name'] = student.name

	return render(request,'student.html',context)
def teacher_view(request):
	context = {}
	if 'login_id' in request.session:
		student = Student.objects.get(login_id=request.session['login_id'])
		context['student_name'] = student.name
		school_students = get_school_dashboard(request.session['login_id'])
		if len(school_students)>0:
			context['school_students'] = school_students
		else:
			messages.error(request,'No Quizes data will be available right now')
	return render(request,'teacher.html',context)

def prepare_quiz(request):
	quiz_id = request.GET['quiz_id']
	quiz = Quiz.objects.get(pk=quiz_id)
	quiz_ser = QuizSerializer(quiz)
	quiz_ser = quiz_ser.data

	quiz_data = loads(dumps(quiz_ser))

	context = {'quiz_data':quiz_data}
	if(request.GET['display'] == 'quiz_details'):
		student_answers = eval(request.GET['student_answers'].replace("u'","'"))
		context['score'] = request.GET['score']
		print (student_answers)
		for question in quiz_data['questions']:
			if str(question['answers'][0]['question']) in student_answers:
				try:
					question['option'] = int(student_answers[str(question['answers'][0]['question'])])
				except Exception as e:
					question['option'] = student_answers[str(question['answers'][0]['question'])]
		#print quiz_data
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
			print( c_ans.answer_text,answers[str(c_ans.question.id)])
			if (c_ans.answer_text == answers[str(c_ans.question.id)]):
				score += 1
		
		StudentAnswers.objects.create(quiz_id=quiz_id,quiz_title=Quiz.objects.get(pk=quiz_id).title,login_id=request.session['login_id'],user_answers=answers,score=score)

		return HttpResponse("<p class='bg-success' style='padding:15px;font-weight:bold;'> Quiz Submitted </br>Result will be available in your Home <i class='glyphicon glyphicon-ok pull-right'></i></p>")

def get_leaderboard():
	quizes = Quiz.objects.all()
	leaders = []
	school_leaders = []
	for quiz in quizes:
		best = StudentAnswers.objects.filter(quiz_id=quiz.id).order_by('-score')
		st_ids = [st.login_id for st in best]
		students = Student.objects.filter(login_id__in=st_ids)
		for st_id in st_ids:
			student = students.get(login_id=st_id)
			leaders.append({'quiz_name':quiz.title,'school_name':student.school.school_name,'score':best.get(login_id=st_id).score,'student_name':student.name,'city_name':student.school.city_name})
			del st_id
		schools = School.objects.all()
		st_ids = [st.login_id for st in best]
		for school in schools:
			students = Student.objects.filter(login_id__in=st_ids).filter(school=school)
			sc_leaders=[]
			for student in students:
				sc_leaders.append({'quiz_name':quiz.title,'school_name':student.school.school_name,'score':best.get(login_id=student.login_id).score,'student_name':student.name})
				del st_ids[st_ids.index(student.login_id)]
			if len(sc_leaders) > 0:
				school_leaders.append(sc_leaders)
	return {'leaders':leaders,'school_leaders':school_leaders}

def get_school_dashboard(login_id):
	quizes = Quiz.objects.all()
	school = Student.objects.get(login_id=login_id).school
	students = SchoolSerializer(school)
	st_ids = {st['login_id']:st['name'] for st in students.data['students']}
	school_students = []
	
	for quiz in quizes:
		quizes_taken=[]
		attempted = StudentAnswers.objects.filter(login_id__in=st_ids.keys(),quiz_id=quiz.id).order_by('-score')
		for attempt in attempted:
			quizes_taken.append({'quiz_id':quiz.id,'student_name':st_ids[attempt.login_id],'login_id':attempt.login_id,'score':attempt.score,'student_answers':attempt.user_answers})
		if len(quizes_taken)>0:
			school_students.append({quiz.title:quizes_taken})
	
	return school_students

def add_school(request):
	if request.method == 'POST':
		form = SchoolForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request,'New School Added')
	else:
		form = SchoolForm()
	return render(request,'add_school.html',{'school_form':form})
