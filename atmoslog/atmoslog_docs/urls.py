from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.docs_index),
	url(r'^getstarted/$', views.getstarted),
	url(r'^webapi/$', views.webapi),
]