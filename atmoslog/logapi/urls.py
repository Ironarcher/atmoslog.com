from django.conf.urls import url

from . import views

urlpatterns = [
	url(r'^(?P<apikey>\w{20})/(?P<tablename>\w{0,50})/(?P<log>{0,200})/$', views.log_view, name='log'),
]