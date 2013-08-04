import unittest
from mock import patch, MagicMock
from controller.helpers import init_component, import_components


class HelpersTests(unittest.TestCase):
    def test_component_init(self):
        """component_init function imports then instantiates a component by its module path."""
        mock_component_class = MagicMock()
        with patch('controller.helpers.import_components', return_value=mock_component_class) as mock_import_components:
            init_component('test.component.path', 'arg', kwarg='kwarg')
            mock_import_components.assert_called_with('test.component.path')
            mock_component_class.assert_called_with('arg', kwarg='kwarg')

    def test_single_component_import(self):
        """A single component is imported by its module path then returned."""
        component_name = 'test.component'
        component_module = MagicMock()
        component_module.Controller = component_name
        with patch('__builtin__.__import__', return_value=component_module) as mock_import:
            imported_controller = import_components(component_name)
            self.assertEqual(imported_controller, component_name)

    def test_multiple_component_import(self):
        """Multiple components are imported and returned at one time, keyed to their module path in a dictionary."""
        component_one = 'test.component_one'
        component_two = 'test.component_two'
        component_module = MagicMock()
        with patch('__builtin__.__import__', return_value=component_module) as mock_import:
            imported_controllers = import_components(component_one, component_two)
            self.assertIn(component_one, imported_controllers)
            self.assertIn(component_two, imported_controllers)
