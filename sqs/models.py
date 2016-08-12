from django.db import models

class School(models.Model):
	sc_id = models.CharField(max_length=100)
	school_name = models.CharField(max_length=100)
	city_name = models.CharField(max_length=100)

	def __str__(self):
		return self.school_name+'/'+self.city_name

class Student(models.Model):
	school = models.ForeignKey(School, related_name="students")
	login_id = models.CharField(max_length=100, unique=True)
	name = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	CHOICES = (('student','student'),('teacher','teacher'))
	user = models.CharField(max_length=100,choices=CHOICES,default="student")

	def __str__(self):
		return self.name


class Quiz(models.Model):
	title = models.CharField(max_length=200,unique=True)
	start_date = models.DateTimeField()
	end_date = models.DateTimeField()
	duration = models.IntegerField()

	def __str__(self):
		return self.title

class Question(models.Model):
	quiz = models.ForeignKey(Quiz, related_name = "questions")
	question_text = models.TextField()
	choice = models.IntegerField()

	def __str__(self):
		return self.question_text

class Answer(models.Model):
	question = models.ForeignKey(Question, related_name = "answers")
	answer_text = models.TextField()
	correct = models.BooleanField()

	def __str__(self):
		return self.answer_text

class StudentAnswers(models.Model):

	quiz_id = models.CharField(max_length=100)
	quiz_title = models.CharField(max_length=100,default='title')
	login_id = models.CharField(max_length=100)
	user_answers = models.CharField(max_length=1000)
	score = models.IntegerField(default=0)

	def __str__(self):
		return self.quiz_id+'/'+self.login_id