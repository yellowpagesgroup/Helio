from django.template.loader import render_to_string
from django.template import RequestContext


def get_request_context(request):
    return RequestContext(request)


def render(template, context, request=None):
    if request:
        return render_to_string(template, context, context_instance=get_request_context(request))

    return render_to_string(template, context)