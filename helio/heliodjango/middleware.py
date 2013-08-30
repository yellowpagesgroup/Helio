from django.core.context_processors import csrf
from django.conf import settings


class CSRFHeaderInject(object):
    """Add CSRF to response without having to use the {% csrf_token %} template tag."""

    def process_response(self, request, response):
        token = unicode(csrf(request)['csrf_token'])

        # Don't inject this as it means the CSRF token is not required
        # and thus this bogus value will override the legit one
        if token != 'NOTPROVIDED':
            response.set_cookie(settings.CSRF_COOKIE_NAME, token, max_age=31449600)
        return response
