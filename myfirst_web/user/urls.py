"""myfirst_web URL Configuration

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
from user import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^login$',views.userlogin,name="login"),
    url(r'^handle$',views.handle,name="handle"),
    url(r'^logout$', views.userlogout, name="logout"),
    url(r'^add_info$',views.add_info,name="add_info"),
    url(r'^forget$',views.forget,name="forget"),
    url(r'^active/(?P<token>.*)$',views.active,name="active"),
    url(r'^register$',views.register,name="register"),
    url(r'^register_handle$',views.register_handle,name="register_handle"),
    url(r'^validatecode$',views.validatecode,name="validatecode"),
    url(r'^user_center_info$',login_required(views.user_center_info),name="user_center_info"),
    url(r'^user_center_order$',login_required(views.user_center_order),name="user_center_order"),
    url(r'^user_center_site$',login_required(views.user_center_site),name="user_center_site"),
    url(r'^province/$', views.province),
    url(r'^city_(\d+)/$', views.city,name='city'),
    url(r'^county_(\d+)/$', views.county,name='city'),
]
