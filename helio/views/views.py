from helio.viewstate.viewstate import ViewStateManager
from helio.settings import VIEWSTATE_MANAGER_SESSION_KEY


def _get_controller_and_view_state_from_session(path, vs_id, session):
    vsm = session[VIEWSTATE_MANAGER_SESSION_KEY]
    vs = vsm.get_view_state(vs_id, no_create=True)
    return vs.controller_from_path(path), vs


def get_view_state(vs_id, session):
    if not VIEWSTATE_MANAGER_SESSION_KEY in session:
        vsm = ViewStateManager()
        session[VIEWSTATE_MANAGER_SESSION_KEY] = vsm

    return session[VIEWSTATE_MANAGER_SESSION_KEY].get_view_state(vs_id)


def get_controller_data(path, vs_id, session, request=None, **kwargs):
    controller, _ = _get_controller_and_view_state_from_session(path, vs_id, session)
    html = controller.render(request=request, **kwargs)
    class_map = controller.class_map_tree({})

    return {'html': html, 'class_map': class_map}


def dispatch_notification(path, vs_id, name, data, session, request=None, **kwargs):
    controller, vs = _get_controller_and_view_state_from_session(path, vs_id, session)
    controller.handle_notification(name, data, request, **kwargs)
    client_notifications = []
    for client_notification in [notification for notification in vs.notification_centre]:
        if client_notification['name'].split(':')[0] == 'load' and client_notification.get('data') is None:
            controller = vs.controller_from_path(client_notification['target'])
            html = controller.render(request=request, **kwargs)
            class_map = controller.class_map_tree({})
            client_notification['data'] = {'html': html, 'class_map': class_map}

        client_notifications.append(client_notification)

    return client_notifications
