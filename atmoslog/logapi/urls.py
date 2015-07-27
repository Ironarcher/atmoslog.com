from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index_view),
	url(r'^(?P<apikey>\w{0,20})/(?P<tablename>\w{0,50})/(?P<log>\w{0,100})/$', views.log_view),
	#url(r'^(?P<apikey>)/$', views.testview),
]