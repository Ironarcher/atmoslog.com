from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^log/', views.log, name='log'),
    url(r'^settings/$', views.settings, name='settings'),
    url(r'^(?P<projectname>)/(?P<tablename>)/$', views.projectlog, name='projectlog')
]