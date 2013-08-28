import unittest
from mock import patch
from django.conf import settings
settings.configure()
from finders import ComponentStaticFinder, ComponentTemplateLoader, walk_component_base_dir


class StaticFinderTests(unittest.TestCase):
    def setUp(self):
        self.finder = ComponentStaticFinder()
        self.finder.component_base_directories = ('MOCK_BASE_DIR', 'MOCK_BASE_DIR_2')

    @patch('helio.heliodjango.finders.exists', return_value=True)
    def test_single_get(self, mock_exists):
        """Static finder converts path in the form path/to/component/component.ext to filesystem path
        <COMPONENTDIR>/path/to/component/static/component.ext."""
        static_path = self.finder.find('path/to/component/component.ext')
        self.assertEqual(static_path, 'MOCK_BASE_DIR/path/to/component/static/component.ext')

    @patch('helio.heliodjango.finders.exists', return_value=False)
    def test_get_failure(self, mock_exists):
        """Trying to get files that don't exist returns an empty tuple."""
        static_path = self.finder.find('can/put/anything/here.js')
        self.assertEqual(static_path, ())

    @patch('helio.heliodjango.finders.exists', return_value=True)
    def test_get_all(self, mock_exists):
        """With get all argument, all the existing files are returned."""
        static_path = self.finder.find('path/to/component/component.ext', all=True)
        self.assertEqual(static_path, ['MOCK_BASE_DIR/path/to/component/static/component.ext',
                                       'MOCK_BASE_DIR_2/path/to/component/static/component.ext'])

    def test_invalid_path_get(self):
        """Getting a path with < 2 components (i.e. not valid for a controller, so no point looking for it)
        should return and not raise any errors."""
        static_path = self.finder.find('file.ext')
        self.assertIsNone(static_path)

    @patch('re.compile')
    def test_wildcard_start_regex_generation(self, mock_re_compile):
        """An ignore_pattern that starts with a * should per converted a regex that ends with $"""
        self.finder.component_base_directories = ()
        for _ in self.finder.list(['*wildcard.start']):  # generators gonna generate
            pass
        mock_re_compile.assert_called_with('wildcard\\.start$')

    @patch('re.compile')
    def test_wildcard_end_regex_generation(self, mock_re_compile):
        """An ignore_pattern that ends with a * should per converted a regex that starts with ^"""
        self.finder.component_base_directories = ()
        for _ in self.finder.list(['wildcard.end*']):  # generators gonna generate
            pass
        mock_re_compile.assert_called_with('^wildcard\\.end')

    @patch('re.compile')
    def test_standard_regex_compile(self, mock_re_compile):
        """A standard regex (i.e. not a wildcard string prentending to be a regex) should be compiled without change."""
        self.finder.component_base_directories = ()
        for _ in self.finder.list(['normal regex.*with middle']):  # generators gonna generate
            pass
        mock_re_compile.assert_called_with('normal regex.*with middle')

    @patch('helio.heliodjango.finders.walk', return_value=(
        ('component/static', [], []),
        ('component2', [], []))
    )
    def test_walk_component_base_dir(self, mock_walk):
        """walk_component_base_dir walks the given directory, returning only 'static' directories and their children."""
        static_dirs = [static_dir for static_dir in walk_component_base_dir('mock')]
        self.assertEqual(len(static_dirs), 1)
        self.assertEqual(static_dirs[0][0], 'component/static')

    @patch('helio.heliodjango.finders.walk_component_base_dir', return_value=(
        ('/component_name/static/', [], ('file.js',)),
        ('/component_name/sub_component/', [], ('anotherfile.ext',)),
        ('/component_name/sub_component/static/', [], ('file2.js', 'file3.css', 'ignore.me')))
    )
    def test_component_static_list(self, mock_walk):
        """The list function should skip directories that aren't 'static' dirs, and files that match the ignore list."""
        self.finder.component_base_directories = ('MOCK_BASE_DIR',)
        static_files = [static_file for static_file in self.finder.list(['^ignore'])]
        self.assertEqual(len(static_files), 3)

        self.assertEqual(static_files[0][1].location, '/component_name/static')
        self.assertEqual(static_files[1][1].location, '/component_name/sub_component/static')
        self.assertEqual(static_files[2][1].location, '/component_name/sub_component/static')

        self.assertEqual(static_files[0][0], 'file.js')
        self.assertEqual(static_files[1][0], 'file2.js')
        self.assertEqual(static_files[2][0], 'file3.css')


class TemplateLoaderTests(unittest.TestCase):
    def setUp(self):
        self.loader = ComponentTemplateLoader()
        self.loader.component_base_directories = ('MOCK_BASE_DIR', 'MOCK_BASE_DIR_2')

    def test_non_nested_template_source_generation(self):
        """Non-nested components are expected to have a template of the same name in the same directory as the
        Controller"""
        sources = [source for source in self.loader.get_template_sources('component.html')]

        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0], 'MOCK_BASE_DIR/component/component.html')
        self.assertEqual(sources[1], 'MOCK_BASE_DIR_2/component/component.html')

    def test_nested_template_source_generation(self):
        """Nested components should use the dotted component name to identify the component directory, and then / to
        identify the template within."""
        sources = [source for source in self.loader.get_template_sources('component.child.html')]
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0], 'MOCK_BASE_DIR/component/child/child.html')
        self.assertEqual(sources[1], 'MOCK_BASE_DIR_2/component/child/child.html')

        sources = [source for source in self.loader.get_template_sources('deeply.nested.component.and.child.html')]
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0], 'MOCK_BASE_DIR/deeply/nested/component/and/child/child.html')
        self.assertEqual(sources[1], 'MOCK_BASE_DIR_2/deeply/nested/component/and/child/child.html')

        sources = [source for source in self.loader.get_template_sources('component.child/another.html')]
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0], 'MOCK_BASE_DIR/component/child/another.html')
        self.assertEqual(sources[1], 'MOCK_BASE_DIR_2/component/child/another.html')
