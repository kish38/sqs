from django.shortcuts import render,render_to_response
from django.http import HttpResponse

from .forms import StudentForm
from .models import Student

def index(request):
	return render_to_response('index.html',{})

def register(request):
	if request.method == "POST":
		form = StudentForm(request.POST)
		if form.is_valid():
			post = form.save(commit=False)
			post.save()
			return HttpResponse('Success')
	else:
		form = StudentForm()
	return render(request,'register.html',{'form':form})