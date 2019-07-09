# -*- coding: utf-8 -*-

""" Views for ddionrails.workspace app: User related views """
from django.core.handlers.wsgi import WSGIRequest
from django.http import HttpResponse
from django.http.response import HttpResponseRedirect
from django.shortcuts import redirect, render

from ddionrails.workspace.forms import UserCreationForm


# request is a required parameter
def account_overview(request: WSGIRequest):  # pylint: disable=unused-argument
    """ Account overview """
    if request.user.is_authenticated:
        context = dict(user=request.user)
        return render(request, "workspace/account.html", context=context)
    return HttpResponse("Unauthorized", status=401)


# request is a required parameter
def register(request: WSGIRequest):  # pylint: disable=unused-argument
    """ Registration view """
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/")
    else:
        form = UserCreationForm()
    context = dict(form=form)
    return render(request, "registration/register.html", context=context)


# request is a required parameter
def user_delete(
    request: WSGIRequest  # pylint: disable=unused-argument
) -> HttpResponseRedirect:
    """ Delete view for auth.User model """
    request.user.delete()
    return redirect("/workspace/logout/")
