from django.shortcuts import render,render_to_response
from django.http import HttpResponse

from .forms import StudentForm
from .models import Student

from django.contrib import messages

def index(request):
	return render_to_response('index.html',{})

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