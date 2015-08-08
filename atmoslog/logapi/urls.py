from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^$', views.index_view),
	#TODO: change the log to allow all characters (not only alphanumeric)
	url(r'^log/(?P<apikey>\w{20})/(?P<tablename>\w{3,50})/(?P<log>.{1,100})/$', views.log_view),
	url(r'^status/(?P<apikey>\w{20})/$', views.status_view),
	url(r'^createtable/(?P<apikey>\w{20})/(?P<tablename>\w{3,50})/$', views.createtable_view),
	url(r'^bulklog/(?P<apikey>\w{20})/(?P<tablename>\w{0,50})/(?P<log>.{1,100000})/$', views.bulklog_view),
	#url(r'^(?P<apikey>)/$', views.testview),
]