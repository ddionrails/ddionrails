from django.http.request import HttpRequest
from django.urls import re_path
from django.http import JsonResponse
from config.urls import urlpatterns as old_urlpatterns
from django.views.decorators.csrf import csrf_exempt
import requests


@csrf_exempt
def elastic_request(request: HttpRequest):
    path = request.path
    target = f"http://nginx{path}"
    response = requests.post(target, headers=request.headers, data=request.body)
    return JsonResponse(response.json(), status=response.status_code)


urlpatterns = old_urlpatterns + [re_path(r"^elastic.*$", elastic_request, name="elastic")]
