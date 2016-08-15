"""sqs URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin

import views

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',views.index),
    url(r'^register$',views.register),
    url(r'^login$',views.login),
    url(r'^student$',views.student_view),
    url(r'^prepare_quiz$',views.prepare_quiz),
    url(r'^submit_quiz$',views.submit_quiz),
    url(r'^teacher$',views.teacher_view),
    url(r'^logout$',views.logout),
    url(r'^sqsadmin/$',views.admin),
    url(r'^sqsadmin/quiz_setup$',views.quiz_setup),
    url(r'^sqsadmin/add_school$',views.add_school),
    url(r'^sqsadmin/csv_upload$',views.csv_upload),

]
