from viewstate import ViewState


class NotificationCentre(object):
    """NotificationCentre is used to send notifications between controllers,
    and to queue notifications for the client."""
    def __init__(self, view_state):
        if not isinstance(view_state, ViewState):
            raise TypeError("view_state must be an instance of ViewState")

        self._view_state = view_state
        view_state.notification_centre = self

        self._notification_queue = []
        self._notification_listeners = {}

    @property
    def view_state(self):
        return self._view_state

    def subscribe_to_notification(self, notification_name, controller_path, source_controller_path='__global__'):
        if not notification_name in self._notification_listeners:
            self._notification_listeners[notification_name] = {}

        if not source_controller_path in self._notification_listeners[notification_name]:
            self._notification_listeners[notification_name][source_controller_path] = set()

        self._notification_listeners[notification_name][source_controller_path].add(controller_path)

    def post_notification(self, notification_name, source_controller_path='__global__', data=None):
        if not notification_name in self._notification_listeners:
            return

        listeners = self._notification_listeners[notification_name].get(source_controller_path, set())

        # always send to global listeners even if a path provided
        if source_controller_path != '__global__' and '__global__' in self._notification_listeners[notification_name]:
            listeners.update(self._notification_listeners[notification_name]['__global__'])

        for controller_path in list(listeners):
            controller = self.view_state.controller_from_path(controller_path)

            if controller is None:
                continue

            controller.handle_notification(notification_name, data)

    def unsubscribe_from_notification(self, notification_name, controller_path, source_controller_path='__global__'):
        if not notification_name in self._notification_listeners:
            return

        if not source_controller_path in self._notification_listeners[notification_name]:
            return

        self._notification_listeners[notification_name][source_controller_path].discard(controller_path)

    def unsubscribe_from_all_notifications(self, controller_path):
        """Unsubscribe a controller from all listeners, useful when a controller is going to be taken off the VS tree."""
        notifications_to_remove = []

        for notification_name, sources in self._notification_listeners.iteritems():
            sources_to_remove = []

            for source_path, listeners in sources.iteritems():
                listeners.discard(controller_path)

                if len(listeners) == 0:
                    sources_to_remove.append(source_path)

            for source_path in sources_to_remove:
                del sources[source_path]

            if len(sources) == 0:
                notifications_to_remove.append(notification_name)

        for notification_name in notifications_to_remove:
            del self._notification_listeners[notification_name]

    def queue_client_notification(self, notification_name, controller_path, data=None, force=False):
        """Queue a notification to be delivered to a specific controller in the client. By default, the same notification
        (i.e. same name, path and data) won't be queued twice in a row, but will if force is True."""
        notification = {'name': notification_name, 'target': controller_path}
        if data is not None:
            notification['data'] = data

        if not force and len(self._notification_queue) and self._notification_queue[-1] == notification:
            return

        self._notification_queue.append(notification)

    def queue_load(self, controller_path, scroll_top=False):
        self.queue_client_notification('load' + (':scroll_top' if scroll_top else ''), controller_path)

    def _client_notification_iterator(self):
        while len(self._notification_queue):
            yield self._notification_queue.pop(0)

    def __iter__(self):
        return self._client_notification_iterator()
