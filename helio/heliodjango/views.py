from helio.views.views import get_view_state, get_controller_data, dispatch_notification
from django.http import HttpResponse
import json


def helio_get_view_state(request):
    try:
        vs_id = int(request.GET.get('vs_id'))
    except TypeError:
        vs_id = -1

    view_state = get_view_state(vs_id, request.session)
    request.session.save()
    return HttpResponse(str(view_state.index))


def helio_get_controller_data(request, controller_path):
    controller_data = get_controller_data(controller_path, int(request.GET.get('vs_id')), request.session, request)

    return HttpResponse(json.dumps(controller_data))


def helio_dispatch_notification(request, controller_path, notification_name):
    notifications = dispatch_notification(controller_path, int(request.GET.get('vs_id')), notification_name,
                                          request.POST, request.session, request)

    return HttpResponse(json.dumps(notifications))
