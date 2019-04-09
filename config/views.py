from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from urllib3 import PoolManager

from ddionrails.studies.models import Study

http = PoolManager()


def bad_request(request, exception):
    response = render(request, "400.html")
    response.status_code = 400
    return response


def permission_denied(request, exception):
    response = render(request, "403.html")
    response.status_code = 403
    return response


def page_not_found(request, exception):
    response = render(request, "404.html")
    response.status_code = 404
    return response


def server_error(request):
    response = render(request, "500.html")
    response.status_code = 500
    return response


class HomePageView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["study_list"] = Study.objects.all()
        context["settings"] = settings
        context["debug_string"] = "Settings: %s" % settings.SETTINGS_MODULE
        return context


def quick_page(request):
    return render(request, "pages/quick.html")


def imprint_page(request):
    return render(request, "pages/imprint.html")


def contact_page(request):
    return render(request, "pages/contact.html")


def elastic_test(request):
    return render(request, "elastic_test.html")


@csrf_exempt
def elastic_proxy(request, path):
    r = http.request("GET", "http://localhost:9200/%s" % path, body=request.body)
    return HttpResponse(r.data)
