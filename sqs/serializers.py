from rest_framework import serializers
from models import School,Student,Quiz,Question,Answer
from django.db import models

class StudentSerializer(serializers.ModelSerializer):
	class Meta:
		model = Student
		fields = ('login_id','name')

class SchoolSerializer(serializers.ModelSerializer):
	students = StudentSerializer(many=True,read_only=True)
	class Meta:
		model = School
		fields = ('sc_id','school_name','city_name','students')

class AnswerSerializer(serializers.ModelSerializer):
	class Meta:
		model = Answer
		fields = ('question','answer_text','correct')
		
class QuestionSerializer(serializers.ModelSerializer):
	answers = AnswerSerializer(many=True, read_only=True)
	class Meta:
		model = Question
		fields = ('quiz','question_text','choice','answers')

class QuizSerializer(serializers.ModelSerializer):
	questions = QuestionSerializer(many=True, read_only=True)

	class Meta:
		model = Quiz
		fields = ('title','start_date','end_date','duration','questions')