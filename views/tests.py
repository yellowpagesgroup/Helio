import unittest
from mock import MagicMock, patch
from views import get_view_state, get_controller_data, dispatch_notification
from settings import VIEWSTATE_MANAGER_SESSION_KEY


class GetViewStateTests(unittest.TestCase):
    def test_adds_vsm_to_session(self):
        """VSM should be added to session in the VIEWSTATE_MANAGER_SESSION_KEY key if it's not
        already there."""
        session = {}
        get_view_state(0, session)
        self.assertIn(VIEWSTATE_MANAGER_SESSION_KEY, session)

        mock_vsm = MagicMock()

        session = {VIEWSTATE_MANAGER_SESSION_KEY: mock_vsm}
        get_view_state(0, session)
        self.assertEqual(session[VIEWSTATE_MANAGER_SESSION_KEY], mock_vsm)

    def test_vsm_call(self):
        """If the VSM can't link the requested viewstate (maybe it is out of range or already linked) then an new VS
        should be created, it should be linked, and its index returned."""
        session = {VIEWSTATE_MANAGER_SESSION_KEY: MagicMock()}
        session[VIEWSTATE_MANAGER_SESSION_KEY].get_view_state = MagicMock(return_value='viewstate')
        vs = get_view_state('vs-id', session)
        session[VIEWSTATE_MANAGER_SESSION_KEY].get_view_state.assert_called_with('vs-id')
        self.assertEqual(vs, 'viewstate')


class MockedControllerTest(unittest.TestCase):
    def setUp(self):
        self.mock_vsm = MagicMock()
        self.mock_vs = MagicMock()
        self.mock_controller = MagicMock()
        self.mock_vs.controller_from_path = MagicMock(return_value=self.mock_controller)
        self.mock_vsm.get_view_state = MagicMock(return_value=self.mock_vs)
        self.session = {VIEWSTATE_MANAGER_SESSION_KEY: self.mock_vsm}


class GetControllerDataTests(MockedControllerTest):
    def test_get_controller_data(self):
        """get_controller_data should get the view state from the VSM, retrieve the controller by path, then render
        the controller and its assets."""
        self.mock_controller.render = MagicMock(return_value='controller html')
        self.mock_controller.class_map_tree = MagicMock(return_value='class_map')

        controller_data = get_controller_data('controller.path', 'vs_id', self.session, 'request')

        self.mock_vsm.get_view_state.assert_called_with('vs_id', no_create=True)
        self.mock_vs.controller_from_path.assert_called_with('controller.path')
        self.mock_controller.render.assert_called_with('request')
        self.mock_controller.class_map_tree.assert_called_with({})
        self.assertEqual({'html': 'controller html', 'class_map': 'class_map'}, controller_data)


class ProcessNotificationTests(MockedControllerTest):
    def test_process_notification(self):
        """process_notification should get the target controller, call process_notification on it with the notification
        name, data and request, then return a list of queued events"""
        notification_data = {'data': ['some', 'data']}
        notification_centre = MagicMock()
        self.mock_vs.notification_centre = notification_centre
        notifications = ['message1', 'message2']
        notification_centre.__iter__ = MagicMock(return_value=iter(notifications))
        self.mock_controller.handle_notification = MagicMock()
        queued_notifications = dispatch_notification('controller.path', 'vs_id', 'notification-name', notification_data,
                                                    self.session, 'request')
        self.mock_vsm.get_view_state.assert_called_with('vs_id', no_create=True)
        self.mock_vs.controller_from_path.assert_called_with('controller.path')
        self.mock_controller.handle_notification.assert_called_with('notification-name', notification_data, 'request')
        self.assertEqual(queued_notifications, notifications)

