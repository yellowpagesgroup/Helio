import unittest
from mock import patch, MagicMock
try:
    from views import helio_get_view_state, helio_get_controller_data, helio_dispatch_notification

    class MockSession(dict):
        def __init__(self):
            super(MockSession, self).__init__()
            self.save = MagicMock()

    class MockRequest(MagicMock):
        def __init__(self):
            super(MockRequest, self).__init__()
            self.GET = {}
            self.POST = {}
            self.session = MockSession()

    class MockViewState(object):
        index = 1

    class DjangoViewTests(unittest.TestCase):
        @patch('helio.heliodjango.views.get_view_state', return_value=MockViewState())
        def test_get_viewstate_call(self, mock_gvs):
            """When a vs_id is not supplied by the client, Helio should get -1"""
            req = MockRequest()
            resp = helio_get_view_state(req)
            mock_gvs.assert_called_with(-1, req.session)
            req.session.save.assert_called_with()
            self.assertEqual(resp.content, '1')

        @patch('helio.heliodjango.views.get_view_state', return_value=MockViewState())
        def test_get_viewstate_call_with_vs_id(self, mock_gvs):
            """When a vs_id is supplied by the client, Helio should try to get it"""
            req = MockRequest()
            req.GET['vs_id'] = '2'
            resp = helio_get_view_state(req)
            mock_gvs.assert_called_with(2, req.session)
            self.assertEqual(resp.content, '1')

        @patch('helio.heliodjango.views.get_controller_data', return_value={'data': 'somedata'})
        def test_get_controller_data_call(self, mock_gcd):
            """Django helio_get_controller_data view should call get_controller_data Helio view with the supplied controller
            path and vs_id"""
            req = MockRequest()
            req.GET['vs_id'] = '3'
            resp = helio_get_controller_data(req, 'controller.path')
            mock_gcd.assert_called_with('controller.path', 3, req.session, req)
            self.assertEqual(resp.content, '{"data": "somedata"}')

        @patch('helio.heliodjango.views.dispatch_notification', return_value={'notification': 'get busy'})
        def test_dispath_notifcation_call(self, mock_dn):
            """Django helio_dispatch_notification view should call dispatch_notification Helio view with the supplied
            controller path, vs_id, notification and data"""
            req = MockRequest()
            req.GET['vs_id'] = '4'
            req.POST = {'exampledata': 'get the data'}
            resp = helio_dispatch_notification(req, 'controller.to.notify', 'notification_name')
            mock_dn.assert_called_with('controller.to.notify', 4, 'notification_name', req.POST, req.session, req)
            self.assertEqual(resp.content, '{"notification": "get busy"}')

except ImportError:
    raise RuntimeWarning("Not testing Django Views")