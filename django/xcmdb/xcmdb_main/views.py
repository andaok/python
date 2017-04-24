from django.shortcuts import render


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
	pass


def manage_host(request):
	pass


def query_service(request):
	pass


def exec_job(request):
	pass


def help_service(request):
	pass

