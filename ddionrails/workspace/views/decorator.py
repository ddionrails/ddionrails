# -*- coding: utf-8 -*-

""" Views for ddionrails.workspace app: Decorator """

from django.core.exceptions import PermissionDenied
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import get_object_or_404

from ddionrails.workspace.models import Basket


def own_basket_only(view):
    """Decorator for basket-related views."""

    def wrapper(request: WSGIRequest, basket_id: int, *args, **kwargs):
        basket = get_object_or_404(Basket, pk=basket_id)
        if basket.user == request.user:
            return view(request, basket_id, *args, **kwargs)
        else:
            raise PermissionDenied

    return wrapper
