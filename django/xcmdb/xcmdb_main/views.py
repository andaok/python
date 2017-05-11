from django.shortcuts import render
from xcmdb_main.forms import AddHostForm


def index(request):

	response = render(request,'xcmdb_main/index.html',{})
	return response


def auth_login(request):
	pass


def auth_logout(request):
	pass


def global_sum(request):
	pass


def add_host(request):
	form = AddHostForm()

	if request.method == 'POST':
		print request.POST

	return render(request,'xcmdb_main/add_host.html',{'form':form})


def manage_host(request):
	pass


def query_service(request):
	pass


def exec_job(request):
	pass


def help_service(request):
	pass

