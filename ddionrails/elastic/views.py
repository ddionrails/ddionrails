# -*- coding: utf-8 -*-

""" Views for ddionrails.elastic app """

from django.shortcuts import render


def angular(request):
    return render(request, "elastic/angular.html")
