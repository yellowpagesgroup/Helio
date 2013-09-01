import unittest
from finders import component_template_to_path, component_static_to_path


class FinderTests(unittest.TestCase):
    def test_standard_template_path_gen(self):
        """component_template_to_path generates path to template (relative to component dir) when no / in name"""
        relative_path = component_template_to_path('my.component.name.html')
        self.assertEqual(relative_path, 'my/component/name/name.html')

    def test_slash_template_path_gen(self):
        """component_template_to_path generates path to template (relative to component dir) when is / in name"""
        relative_path = component_template_to_path('my.component.name/anothertemplate.html')
        self.assertEqual(relative_path, 'my/component/name/anothertemplate.html')

    def test_component_static_path_gen(self):
        """component_static_to_path generates path to template (relative to component dir)"""
        relative_path = component_static_to_path('my/component/name/name.js')
        self.assertEqual(relative_path, 'my/component/name/static/name.js')

        relative_path = component_static_to_path('my/component/name/other.js')
        self.assertEqual(relative_path, 'my/component/name/static/other.js')

        relative_path = component_static_to_path('component.js')
        self.assertIsNone(relative_path)
