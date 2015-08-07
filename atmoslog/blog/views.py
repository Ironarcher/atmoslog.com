from django.shortcuts import render
from .models import Post

# Create your views here.

def index(request):
	post_list = Post.objects.order_by('-pub_date')[:5]
	context = {
		"post_list" : post_list, 
	}
	return render(request, 'blog/blog.html', context)