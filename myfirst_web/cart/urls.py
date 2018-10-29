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

from cart import views


urlpatterns = [
    url(r'^add$',views.add,name="add"),
    url(r'^show_cart_count$', views.show_cart_count, name="show_cart_count"),
    url(r'^show_cart$',views.show_cart,name="show_cart"),
    url(r'^update_cart$',views.updata_cart,name="update_cart"),
    url(r'^delete$',views.delete,name="delete"),
]
