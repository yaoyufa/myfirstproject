from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
def login_user(func):
    def inner(*args,**kwargs):
        if args[0].session.get("session1"):
            return func(*args,**kwargs)
        else:
            resp=redirect(reverse("area:login"))
            resp.set_cookie("url_dest",args[0].get_full_path())
            return resp
    return inner