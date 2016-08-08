from django.db import models

class School(models.Model):
	sc_id = models.CharField(max_length=100)
	school_name = models.CharField(max_length=100)
	city_name = models.CharField(max_length=100)

	def __str__(self):
		return self.school_name+'/'+self.city_name

class Student(models.Model):
	student_id = models.CharField(max_length=100)
	name = models.CharField(max_length=100)
	password = models.CharField(max_length=100)
	school = models.ForeignKey(School)

	def __str__(self):
		return self.name