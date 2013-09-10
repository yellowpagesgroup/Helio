import unittest
from mock import patch
try:
    import flask
    from werkzeug.datastructures import ImmutableMultiDict
    from helioflask import helioflask, template_env

    flask.session = {}

    class MockViewState(object):
        index = 1

        def __init__(self, index=1):
            self.index = index

    class FlaskBlueprintTests(unittest.TestCase):
        def setUp(self):
            self.app = flask.Flask(__name__)
            self.app.secret_key = 'secret'
            self.app.register_blueprint(helioflask)
            self.client = self.app.test_client()

        @patch('helio.helioflask.helioflask.get_view_state', return_value=MockViewState())
        def test_get_viewstate_call(self, mock_gvs):
            """When a vs_id is not supplied by the client, Helio should get -1"""
            with self.app.test_request_context():
                self.client.get('/get-view-state/')
                mock_gvs.assert_called_with(-1, {})

        @patch('helio.helioflask.helioflask.get_view_state', return_value=MockViewState(2))
        def test_get_viewstate_call_with_vs_id(self, mock_gvs):
            """When a vs_id is supplied by the client, Helio should try to get it"""
            with self.app.test_request_context():
                resp = self.client.get('/get-view-state/?vs_id=2')
                mock_gvs.assert_called_with(2, {})
                self.assertEqual(resp.data, '2')

        @patch('helio.helioflask.helioflask.get_controller_data', return_value={'data': 'somedata'})
        def test_get_controller_data_call(self, mock_gcd):
            """Flask helio_get_controller_data view should call get_controller_data Helio view with the supplied controller
            path and vs_id"""
            with self.app.test_request_context():
                resp = self.client.get('/controller/controller.path?vs_id=3')
                mock_gcd.assert_called_with('controller.path', 3, flask.session, flask.request,
                                            environment=template_env)
                self.assertEqual(resp.data, '{"data": "somedata"}')

        @patch('helio.helioflask.helioflask.dispatch_notification', return_value={'notification': 'get busy'})
        def test_dispatch_notification_call(self, mock_dn):
            """Flask helio_dispatch_notification view should call dispatch_notification Helio view with the supplied
            controller path, vs_id, notification and data"""
            with self.app.test_request_context():
                post_data = {'exampledata': 'get the data'}
                resp = self.client.post('/notification/controller.to.notify/notification_name?vs_id=4', data=post_data)
                mock_dn.assert_called_with('controller.to.notify', 4, 'notification_name',
                                           ImmutableMultiDict(post_data), flask.session, flask.request,
                                           environment=template_env)
                self.assertEqual(resp.data, '{"notification": "get busy"}')

        @patch('helio.helioflask.helioflask.abort')
        def test_flask_static_invalid_url_error(self, mock_abort):
            """Test that abort(404) is called if a static path contains '..' (paths starting with / are automatically
            stripped of starting / it seems."""
            with self.app.test_request_context():
                self.client.get('/heliostatic/bad/../path')
                mock_abort.assert_called_with(404)

        @patch('helio.helioflask.helioflask.exists', return_value=True)
        @patch('helio.helioflask.helioflask.isdir', return_value=False)
        @patch('helio.helioflask.helioflask.send_file')
        @patch('helio.helioflask.helioflask.STATICFILES_DIRS', ('STATIC_DIR',))
        def test_flask_helio_staticfiles_get(self, mock_send_file, mock_isdir, mock_exists):
            """Test that the helio static files are returned by priority"""
            with self.app.test_request_context():
                self.client.get('/heliostatic/file.js')
                mock_send_file.assert_called_with('STATIC_DIR/file.js')

        @patch('helio.helioflask.helioflask.component_static_to_path', return_value="file/static/file.js")
        @patch('helio.helioflask.helioflask.exists', return_value=False)
        @patch('helio.helioflask.helioflask.isdir', return_value=False)
        @patch('helio.helioflask.helioflask.send_file')
        @patch('helio.helioflask.helioflask.abort')
        @patch('helio.helioflask.helioflask.STATICFILES_DIRS', ('STATIC_DIR',))
        @patch('helio.helioflask.helioflask.helio.settings.COMPONENT_BASE_DIRECTORIES', ('COMPONENT_DIR',))
        def test_non_existant_non_get(self, mock_abort, mock_send_file, mock_isdir, mock_exists, mock_csp):
            """If a file does not exist it should not be sent"""
            with self.app.test_request_context():
                self.client.get('/heliostatic/file.js')
                mock_send_file.assert_not_called()
                mock_abort.assert_called_with(404)

        @patch('helio.helioflask.helioflask.exists', return_value=True)
        @patch('helio.helioflask.helioflask.isdir', return_value=True)
        @patch('helio.helioflask.helioflask.send_file')
        @patch('helio.helioflask.helioflask.STATICFILES_DIRS', ('STATIC_DIR',))
        @patch('helio.helioflask.helioflask.helio.settings.COMPONENT_BASE_DIRECTORIES', ('COMPONENT_DIR',))
        def test_isdir_non_get(self, mock_send_file, mock_isdir, mock_exists):
            """If a file does is a dir don't send it."""
            with self.app.test_request_context():
                self.client.get('/heliostatic/file.js')
                mock_send_file.assert_not_called()

        @patch('helio.helioflask.helioflask.component_static_to_path', return_value="file/static/file.js")
        @patch('helio.helioflask.helioflask.exists', return_value=True)
        @patch('helio.helioflask.helioflask.isdir', return_value=False)
        @patch('helio.helioflask.helioflask.send_file')
        @patch('helio.helioflask.helioflask.STATICFILES_DIRS', ())
        @patch('helio.helioflask.helioflask.helio.settings.COMPONENT_BASE_DIRECTORIES', ('COMPONENT_DIR',))
        def test_component_static_get(self, mock_send_file, mock_isdir, mock_exists, mock_csp):
            """If the file is not a helio static, get it from the component dir."""
            with self.app.test_request_context():
                self.client.get('/heliostatic/file.js')
                mock_csp.assert_called_with('file.js')
                mock_send_file.called_with('COMPONENT_DIR/file/static/file.js')

except ImportError:
    raise RuntimeWarning("Not testing Flask integration.")