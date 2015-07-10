from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    #url('^', include('django.contrib.auth.urls')),
    url(r'^settings/', views.settings, name='settings'),
    url(r'^log/', views.log, name='log')
]