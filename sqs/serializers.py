from rest_framework import serializers
from models import School,Student
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
