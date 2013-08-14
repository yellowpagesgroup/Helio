import unittest
from mock import MagicMock
from notification import NotificationCentre
from viewstate import ViewState


class NotifcationCentreTests(unittest.TestCase):
    def test_notification_invalid_viewstate_init(self):
        """NC must be instantiated with a ViewState (or subclass)."""
        not_a_viewstate = object()

        with self.assertRaises(TypeError):
            NotificationCentre(None)

        with self.assertRaises(TypeError):
            NotificationCentre(not_a_viewstate)

    def test_viewstate_cannot_be_set(self):
        """ViewState is read only and can not be set once the NC is instantiated."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)
        new_v = ViewState(MagicMock())

        with self.assertRaises(AttributeError):
            n.view_state = new_v

    def test_viewstate_read(self):
        """ViewState can be read from the NC."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)
        self.assertEqual(v, n.view_state)

    def test_symbiotic_relationship(self):
        """v.notification_centre -> nc, and nc.view_state -> vs."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)
        self.assertEqual(n.view_state, v)
        self.assertEqual(v.notification_centre, n)

    def test_global_notification_subscription_and_receive(self):
        """A component that subscribes to a notification with a blank source, should receive that notification no matter
        what source posts it."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)
        component = MagicMock()
        v.component_from_path = MagicMock(return_value=component)

        n.subscribe_to_notification('test_notification', 'page.test_component')
        n.post_notification('test_notification')
        component.process_notification.assert_called_with('test_notification', None)

        n.subscribe_to_notification('test_notification2', 'page.test_component')
        n.post_notification('test_notification2', 'page.another_component')
        component.process_notification.assert_called_with('test_notification2', None)

    def test_specific_notification_subscription_and_receive(self):
        """A component can listen to events from only single sources, so shouldn't receive that notification if posted
        from elsewhere."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)
        component = MagicMock()
        v.component_from_path = MagicMock(return_value=component)

        n.subscribe_to_notification('test_notification', 'page.test_component', 'page.source_component')
        n.post_notification('test_notification')
        n.post_notification('test_notification', 'page.another_source')
        self.assertEqual(component.process_notification.call_count, 0)

        n.post_notification('test_notification', 'page.source_component')
        component.process_notification.assert_called_with('test_notification', None)

    def test_missing_component_no_exception(self):
        """If a component no longer exists at the path to receive the notification, no error should occur."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)
        v.component_from_path = MagicMock(return_value=None)
        n.subscribe_to_notification('test_notification', 'page.test_component')
        n.post_notification('test_notification')

    def test_no_listeners_no_exception(self):
        """If there is no listener for a notification, no error should occur."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)
        n.post_notification('test_notification')

    def test_notification_unsubscribe(self):
        """After a component unsubscribes, it should not receive that notification any more (but should still receive
        others that it is subscribed to)."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)
        component = MagicMock()
        v.component_from_path = MagicMock(return_value=component)

        n.subscribe_to_notification('test_notification', 'page.test_component')
        n.subscribe_to_notification('test_notification2', 'page.test_component')
        n.unsubscribe_from_notification('test_notification', 'page.test_component')
        n.post_notification('test_notification')
        self.assertEqual(component.process_notification.call_count, 0)
        n.post_notification('test_notification2')
        component.process_notification.assert_called_with('test_notification2', None)

    def test_notification_unsubscribe_all(self):
        """nc.unsubscribe_from_all_notifications should prevent any more calls going to the component."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)
        component = MagicMock()
        v.component_from_path = MagicMock(return_value=component)

        n.subscribe_to_notification('test_notification', 'page.test_component')
        n.subscribe_to_notification('test_notification2', 'page.test_component')
        n.unsubscribe_from_all_notifications('page.test_component')
        n.post_notification('test_notification')
        n.post_notification('test_notification2')
        self.assertEqual(component.process_notification.call_count, 0)

    def test_client_notification_queue_and_retrieve(self):
        """Client notifications are queued and retrieved in FIFO order."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)

        n.queue_client_notification('test_name', 'page.test_component')
        n.queue_client_notification('test_name2', 'page.test_component2', 'somedata')

        # notifications are retrieved FIFO
        queued_notifications = [notification for notification in n]
        self.assertEqual(len(queued_notifications), 2)
        self.assertEqual({'name': 'test_name', 'path': 'page.test_component'}, queued_notifications[0])
        self.assertEqual({'name': 'test_name2', 'path': 'page.test_component2', 'data': 'somedata'},
                         queued_notifications[1])

        # queue should now be empty
        self.assertEqual(len([notification for notification in n]), 0)

    def test_same_notification_multiple_queue(self):
        """The same notification will not be queued twice, however if any of name, path or data differs, it will."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)

        n.queue_client_notification('test_name', 'page.test_component')
        n.queue_client_notification('test_name', 'page.test_component')
        self.assertEqual(len([notification for notification in n]), 1)

        n.queue_client_notification('test_name', 'page.test_component')
        n.queue_client_notification('test_name', 'page.test_component', 'somedata')
        self.assertEqual(len([notification for notification in n]), 2)

        n.queue_client_notification('test_name', 'page.test_component2')
        n.queue_client_notification('test_name', 'page.test_component')
        self.assertEqual(len([notification for notification in n]), 2)

        n.queue_client_notification('test_name', 'page.test_component')
        n.queue_client_notification('test_name2', 'page.test_component')
        self.assertEqual(len([notification for notification in n]), 2)

    def test_force_same_notification_multiple_queue(self):
        """The same notification will be queued twice if the force arg is True."""
        v = ViewState(MagicMock())
        n = NotificationCentre(v)

        n.queue_client_notification('test_name', 'page.test_component')
        n.queue_client_notification('test_name', 'page.test_component', force=True)
        queued_notifications = [notification for notification in n]
        self.assertEqual(len(queued_notifications), 2)
        self.assertEqual(queued_notifications[0], queued_notifications[1])