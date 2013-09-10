import unittest
from mock import patch, MagicMock
try:
    from jinja2 import TemplateNotFound
    from finders import ComponentTemplateLoader, real_file_path

    class ComponentTemplateTests(unittest.TestCase):
        rfp = '/path/to/file'

        @patch("helio.helioflask.finders.isdir", return_value=False)
        @patch("helio.helioflask.finders.exists", return_value=True)
        def test_real_file_path_exists(self, mock_exists, mock_isdir):
            """real_file_path should return None if the path exists and is not a dir."""
            rfp = real_file_path(self.rfp)
            mock_exists.assert_called_with(self.rfp)
            mock_isdir.assert_called_with(self.rfp)
            self.assertEqual(rfp, self.rfp)

        @patch("helio.helioflask.finders.isdir", return_value=False)
        @patch("helio.helioflask.finders.exists", return_value=False)
        def test_real_file_path_doesnt_exist(self, mock_exists, mock_isdir):
            """real_file_path should return None if the path does not exist."""
            rfp = real_file_path(self.rfp)
            mock_exists.assert_called_with(self.rfp)
            self.assertIsNone(rfp)

        @patch("helio.helioflask.finders.isdir", return_value=True)
        @patch("helio.helioflask.finders.exists", return_value=True)
        def test_real_file_path_is_dir(self, mock_exists, mock_isdir):
            """real_file_path should return None if the path exists and is a dir."""
            rfp = real_file_path(self.rfp)
            mock_exists.assert_called_with(self.rfp)
            mock_isdir.assert_called_with(self.rfp)
            self.assertIsNone(rfp)

        @patch("helio.helioflask.finders.real_file_path", return_value="path/to/file.html")
        @patch("helio.helioflask.finders.getmtime", return_value=1)
        def test_source_get(self, mock_getmtime, mock_rfp):
            """Should read the template from the component dir and return its content and full path."""
            mock_file = MagicMock()
            with patch("__builtin__.file", mock_file):
                manager = mock_file.return_value.__enter__.return_value
                manager.read.return_value = 'template data'
                loader = ComponentTemplateLoader(('COMPONENT_DIR',))
                source, path, modified_func = loader.get_source(None, 'template.html')
                mock_rfp.assert_called_with('COMPONENT_DIR/template/template.html')
                mock_file.assert_called_with('path/to/file.html')
                mock_getmtime.assert_called_with('path/to/file.html')
                self.assertEqual(path, 'path/to/file.html')
                self.assertEqual(source, 'template data')

        @patch("helio.helioflask.finders.real_file_path", return_value=None)
        def test_source_doesnt_exist(self, mock_rfp):
            """TemplateNotFound should be raised when the template doesn't exist."""
            with self.assertRaises(TemplateNotFound):
                loader = ComponentTemplateLoader(('COMPONENT_DIR',))
                loader.get_source(None, 'template.html')

except ImportError:
    raise RuntimeWarning("Not testing Flask/Jinja2 Template Integration")