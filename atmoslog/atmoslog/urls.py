"""atmoslog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'atmoslog_main.views.index'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^log/', include('tablemanager.urls')),
    #url(r'^about/', include('atmoslog_main.urls')),
    #url(r'^docs/', include('atmoslog_docs.urls')),
    url(r'^settings/$', 'tablemanager.views.settings'),
    url(r'^api/$', include('logapi.views', namespace='api')),

    #User controls
    url(r'^login/$', 'tablemanager.views.login_view'),
    url(r'^logout/$', 'tablemanager.views.logout_view'),
    url(r'^account/$', 'tablemanager.views.user_page'),
    url(r'^register/$', 'tablemanager.views.register_view'),
    url(r'^create/$', 'tablemanager.views.create'),
]
