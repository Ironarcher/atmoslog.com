from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    remember = forms.BooleanField(label='Remember me')

class RegisterForm(forms.Form):
	pass
