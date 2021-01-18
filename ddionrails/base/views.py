from django.template.response import TemplateResponse

from config.settings import base


def imprint(request, template_name="pages/imprint.html"):
    context = {"DEFAULT_FROM_EMAIL": base.DEFAULT_FROM_EMAIL}
    return TemplateResponse(request, template_name, context)
