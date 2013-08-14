import unittest
from mock import patch, MagicMock
from controller.helpers import init_controller, import_controllers


class HelpersTests(unittest.TestCase):
    def test_controller_init(self):
        """init_controller function imports then instantiates a component by its module path."""
        mock_controller_class = MagicMock()
        with patch('controller.helpers.import_controllers', return_value=mock_controller_class) as \
                mock_import_controllers:
            init_controller('test.component.path', 'arg', kwarg='kwarg')
            mock_import_controllers.assert_called_with('test.component.path')
            mock_import_controllers.assert_called_with('arg', kwarg='kwarg')

    def test_single_controller_import(self):
        """A single controller is imported by its module path then returned."""
        component_name = 'test.component'
        component_module = MagicMock()
        component_module.Controller = component_name
        with patch('__builtin__.__import__', return_value=component_module) as mock_import:
            imported_controller = import_controllers(component_name)
            self.assertEqual(imported_controller, component_name)

    def test_multiple_controller_import(self):
        """Multiple controllers are imported and returned at one time, keyed to their module path in a dictionary."""
        component_one = 'test.component_one'
        component_two = 'test.component_two'
        component_module = MagicMock()
        with patch('__builtin__.__import__', return_value=component_module) as mock_import:
            imported_controllers = import_controllers(component_one, component_two)
            self.assertIn(component_one, imported_controllers)
            self.assertIn(component_two, imported_controllers)
