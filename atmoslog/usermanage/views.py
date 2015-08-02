#Imports
from django.shortcuts import render, redirect
from django.http import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

import re
import db_interface

# All views relating to users

def login_view(request):
	status = "started"
	username = password = ""
	next = ""
	if request.GET:
		next = request.GET['next']
		print(next)

	if request.POST:
		first = False
		username = request.POST['username']
		password = request.POST['password']
		user = authenticate(username=username, password=password)
		if user is not None:
			if user.is_active:
				login(request, user)
				status = "success"
				remember = request.POST.getlist('remember[]')
				if "remember" in remember:
					request.session.set_expiry(1209600)
				if next == "":
					return HttpResponseRedirect("/")
				else:
					return HttpResponseRedirect(next)
			else:
				status = "inactive"
		else:
			status = "failed"
	else:
		first = True
	context = {
		"status" : status,
		"first" : first,
		"username_init" : username,
		"password_init" : password,
		"next" : next,
	}
	return render(request, 'usermanage/login.html', context)

def logout_view(request):
	logout(request)
	return HttpResponseRedirect("/")

def register_view(request):
	issues = []
	username = firstname = lastname = password = email = ""
	if request.method == "POST":
		first = False
		username = request.POST['username']
		password = request.POST['password']
		firstname = request.POST['firstname']
		lastname = request.POST['lastname']
		email = request.POST['email']
		if len(username) < 4 or len(username) > 50:
			#Username must be 4-50 characters long
			issues.append("username_length")
		if re.match('^\w+$', username) is None and len(username) != 0:
			#Username can only contain characters and numbers and underscores
			issues.append("username_char")
		if len(password) < 6 or len(password) > 50:
			#Password must be 6-50 characters long
			issues.append("password_length")
		if re.match("^[A-Za-z]*$", firstname) is None:
			#Names can only contain letters and spaces
			issues.append("firstname_char")
		if re.match("^[A-Za-z]*$", lastname) is None:
			#Names can only contain letters and spaces
			issues.append("lastname_char")
		if re.match("^[A-Za-z@.]*$", email) is None or len(email) < 3:
			#Email invalid
			issues.append("email_char")
		if check_user_exists(username):
			#User already exists
			issues.append("username_taken")

		#Sign the user up
		if len(issues) == 0:
			user = User.objects.create_user(username, email, password)
			if len(firstname) != 0:
				user.first_name = firstname
			if len(lastname) != 0:
				user.last_name = lastname
			user.userprofile.about_me = ""
			user.userprofile.fav_language = "?"
			user.save()
			#Redirect the user to the verification process
			#TO-DO
			return HttpResponseRedirect("/")
	else:
		first = True

	context = {
		"issues" : issues,
		"first" : first,
		"username_init" : username,
		"password_init" : password,
		"firstname_init" : firstname,
		"lastname_init" : lastname,
		"email_init" : email,
	}
	return render(request, 'usermanage/register.html', context)

#Login is required to view this page
def user_page(request):
	if request.user.is_authenticated():
		authenticated = True
		user = request.user
		username = request.user.get_username()
		#get the firstname and lastname

		userobj = User.objects.get(username=user)
		firstname = userobj.first_name
		lastname = userobj.last_name
		email = userobj.email
		about_me = ""
		favorite_language = "Python"
		join_date = "Forever"
		#about_me = userobj.get_profile().about_me
		#favorite_language = userobj.userprofile.fav_language
		#join_date = userobj.userprofile.joined_on

		context = {
		"authenticated" : authenticated,
		"user" : user,
		"firstname" : firstname,
		"lastname" : lastname,
		"email" : email,
		"about_me" : about_me,
		"favorite_language" : favorite_language,
		"join_date" : join_date,
		"user_projects" : db_interface.getUserProjects(username),
		}
		return render(request, 'usermanage/account.html', context)
	else:
		return HttpResponseRedirect('/login/?next=/account/')

def changepassword_view(request):
	pass

def reset_view(request):
	pass

def check_user_exists(username):
	if User.objects.filter(username=username).exists():
		return True
	else:
		return False