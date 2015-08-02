from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(?P<projectname>\w{0,50})/(?P<tablename>\w{0,50})/$', views.projectlog,
    	name='projectlog'),
    url(r'^(?P<projectname>\w{0,50})/$', views.project_settings, name='project_settings'),
]