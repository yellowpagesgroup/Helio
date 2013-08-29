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


def get_controller_data(path, vs_id, session, request=None):
    controller, _ = _get_controller_and_view_state_from_session(path, vs_id, session)
    html = controller.render(request=request)
    class_map = controller.class_map_tree({})

    return {'html': html, 'class_map': class_map}


def dispatch_notification(path, vs_id, name, data, session, request=None):
    controller, vs = _get_controller_and_view_state_from_session(path, vs_id, session)
    controller.handle_notification(name, data, request)
    client_notifications = [notification for notification in vs.notification_centre]

    return client_notifications