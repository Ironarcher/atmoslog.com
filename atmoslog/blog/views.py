from django.shortcuts import render
from .models import Post

# Create your views here.

def index(request):
	if request.user.is_authenticated():
		authenticated = True
		user = request.user
	else:
		authenticated = False
		user = None

	post_list = Post.objects.order_by('-pub_date')[:5]
	context = {
		"post_list" : post_list, 
		"authenticated" : authenticated,
		"user" : user,
	}
	return render(request, 'blog/blog.html', context)