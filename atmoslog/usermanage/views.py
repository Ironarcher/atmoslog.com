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
		if re.match("^[A-Za-z0-9@._]*$", email) is None or len(email) < 3:
			#Email invalid
			issues.append("email_char")
		if check_user_exists(username):
			#User already exists
			issues.append("username_taken")
		if check_email_exists(email):
			#Email is already being used
			issues.append("email_taken")

		#Sign the user up
		if len(issues) == 0:
			user = User.objects.create_user(username, email, password)
			if len(firstname) != 0:
				user.first_name = firstname
			if len(lastname) != 0:
				user.last_name = lastname
			user.profile.about_me = ""
			user.profile.fav_language = "?"
			user.profile.addPicture()
			user.profile.start()
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
		if request.method == 'POST':
			if request.POST['formtype'] == "settings":
				edit_aboutme = request.POST['aboutme'][:500]
				edit_programlang = request.POST['programlang']
				edit_country = request.POST['country']
				edit_emailshow = request.POST.getlist('showemail[]')
				if "yes" in edit_emailshow:
					emailshow_final = True
				else:
					emailshow_final = False

				#Commit changes
				userp = request.user.profile 
				userp.about_me = edit_aboutme
				userp.fav_language = edit_programlang
				userp.country = edit_country
				userp.showemail = emailshow_final
				userp.save()
				HttpResponseRedirect('/account/')

		authenticated = True
		user = request.user
		username = request.user.get_username()
		#get the firstname and lastname

		userobj = User.objects.get(username=user)
		firstname = userobj.first_name
		lastname = userobj.last_name
		email = userobj.email
		about_me = userobj.profile.about_me
		favorite_language = userobj.profile.fav_language
		join_date = userobj.profile.joined_on
		profile_picture = userobj.profile.picture
		country = userobj.profile.country

		context = {
		"authenticated" : authenticated,
		"user" : user,
		"firstname" : firstname,
		"lastname" : lastname,
		"email" : email,
		"userp" : userobj.profile,
		"user_projects" : db_interface.getUserProjects(username),
		}
		return render(request, 'usermanage/account.html', context)
	else:
		return HttpResponseRedirect('/login/?next=/account/')

def changepassword_view(request):
	if request.user.is_authenticated():
		issues = []
		oldpassword = newpassword = newpassword_confirm = ""
		if request.method == "POST":
			first = False
			oldpassword = request.POST['oldpassword']
			newpassword = request.POST['newpassword']
			newpassword_confirm = request.POST['newpassword_confirm']
			user = authenticate(username=request.user.get_username(), password=oldpassword)
			if user is None:
				#Wrong old password
				issues.append("wrong_password")
			elif not user.is_active:
				#User is not active
				issues.append("user_inactive")
			if len(newpassword) < 6 or len(newpassword) > 50:
				#Password must be 6-50 characters long
				issues.append("password_length")
			if newpassword != newpassword_confirm:
				#New passwords do not match
				issues.append("password_match")

			#Change the user's password
			if len(issues) == 0:
				user.set_password(newpassword)
				user.save()
				#TODO: Send email that your password has been changed
				#If the password change was not you, reset the account (lock)
				return HttpResponseRedirect("/account/")
		else:
			first = True

		context = {
			"issues" : issues,
			"first" : first,
			"oldpassword_init" : oldpassword,
			"newpassword_init" : newpassword,
			"newpassword_confirm_init" : newpassword_confirm,
		}
		return render(request, 'usermanage/change_password.html', context)
	else:
		return HttpResponseRedirect('/login/?next=/changepassword/')

def reset_view(request):
	pass

def check_user_exists(username):
	if User.objects.filter(username=username).exists():
		return True
	else:
		return False

def check_email_exists(email):
	if User.objects.filter(email=email).exists():
		return True
	else:
		return False

'''
def get_gravatar(user):
	userobj = User.objects.get(username=user)
	email = userobj.email

	#Create url to get the get_profile
	profilepic = 
'''