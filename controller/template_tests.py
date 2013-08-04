import unittest
from template import BaseTemplateLoader


class TemplateLoaderTests(unittest.TestCase):
    def setUp(self):
        self.loader = BaseTemplateLoader()
        self.loader.base_dir = '/test/directory/components/'

    def test_base_component_template_path_generation(self):
        """The loader should convert the template name (based on the components dotted path) into the correct file
        system path."""
        template_name = 'component_name.template_name.html'
        full_path = self.loader.file_path_for_template(template_name)
        self.assertEqual(full_path, '/test/directory/components/component_name/template_name.html')

    def test_base_component_template_extensionless_path_generation(self):
        """The loader should generate the name correctly (as above) even if the file does not have an extension."""
        template_name = 'component_name.template_name'
        full_path = self.loader.file_path_for_template(template_name, False)
        self.assertEqual(full_path, '/test/directory/components/component_name/template_name')

    def test_base_component_template_nested_path_generation(self):
        """The path should be generated correctly (as above) for nested components."""
        template_name = 'super_component.component_name.template_name.html'
        full_path = self.loader.file_path_for_template(template_name)
        self.assertEqual(full_path, '/test/directory/components/super_component/component_name/template_name.html')