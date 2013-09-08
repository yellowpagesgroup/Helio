from os.path import join, exists, isdir, dirname, abspath
import json
from flask import Blueprint, request, abort, send_file, session
from jinja2 import Environment
import helio.settings
from helio.controller.finders import component_static_to_path
from helio.helioflask.finders import ComponentTemplateLoader
from helio.views.views import get_view_state, get_controller_data, dispatch_notification

STATICFILES_DIRS = (
    join(dirname(abspath(helio.settings.__file__)), 'javascript', 'static'),
    join(dirname(abspath(helio.settings.__file__)), 'helioflask', 'static')
)

helioflask = Blueprint('helioflask', __name__)

template_env = Environment(loader=ComponentTemplateLoader(helio.settings.COMPONENT_BASE_DIRECTORIES))

@helioflask.route('/get-view-state/')
def flask_get_view_state():
    try:
        vs_id = int(request.args.get('vs_id'))
    except TypeError:
        vs_id = -1

    view_state = get_view_state(vs_id, session)
    session.modified = True
    return str(view_state.index)


@helioflask.route('/controller/<controller_path>')
def flask_get_controller_data(controller_path):
    controller_data = get_controller_data(controller_path, int(request.args.get('vs_id')), session, request, environment=template_env)
    session.modified = True
    return json.dumps(controller_data)


@helioflask.route('/notification/<controller_path>/<notification_name>', methods=['POST'])
def flask_dispatch_notification(controller_path, notification_name):
    notifications = dispatch_notification(controller_path, int(request.args.get('vs_id')), notification_name,
                                          request.form, session, request,  environment=template_env)
    session.modified = True
    return json.dumps(notifications)


@helioflask.route('/heliostatic/<path:static_path>')
def flask_static_handler(static_path):
    if '..' in static_path or static_path.startswith('/'):
        abort(404)
        return

    for app_static_dir in STATICFILES_DIRS:
        file_path = join(app_static_dir, static_path)
        if exists(file_path) and not isdir(file_path):
            return send_file(file_path)

    for component_dir in helio.settings.COMPONENT_BASE_DIRECTORIES:
        full_path = join(component_dir, component_static_to_path(static_path))

        if exists(full_path):
            return send_file(full_path)

    abort(404)
