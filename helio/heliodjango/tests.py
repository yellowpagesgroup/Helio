import unittest
from mock import patch, MagicMock

try:
    from django.conf import settings
    settings.configure()
    from finders import ComponentStaticFinder, ComponentTemplateLoader, walk_component_base_dir, helio_static_path
    from renderers import render, RequestContext, get_request_context
    from middleware import CSRFHeaderInject

    class StaticFinderTests(unittest.TestCase):
        def setUp(self):
            self.finder = ComponentStaticFinder()
            self.finder.component_base_directories = ('MOCK_BASE_DIR', 'MOCK_BASE_DIR_2')

        @patch('helio.heliodjango.finders.exists', return_value=True)
        @patch('helio.heliodjango.finders.helio_static_path', return_value=None)
        def test_single_get(self, mock_helio_finder, mock_exists):
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
        @patch('helio.heliodjango.finders.helio_static_path', return_value=None)
        def test_get_all(self, mock_helio_finder, mock_exists):
            """With get all argument, all the existing files are returned."""
            static_paths = self.finder.find('path/to/component/component.ext', all=True)
            self.assertEqual(static_paths, ['MOCK_BASE_DIR/path/to/component/static/component.ext',
                                           'MOCK_BASE_DIR_2/path/to/component/static/component.ext'])

        @patch('helio.heliodjango.finders.component_static_to_path', return_value=None)
        @patch('helio.heliodjango.finders.exists', return_value=True)
        @patch('helio.heliodjango.finders.helio_static_path', return_value='helio/static.js')
        def test_helio_staticdirs_get_all(self, mock_helio_finder, mock_exists, mock_csp):
            """With get all argument, and when helio_static_dirs is defined, should return from the helio_static_dirs
            first."""
            self.finder.helio_static_dirs = ['/javascript']
            self.finder.component_base_directories = []
            static_paths = self.finder.find('path/to/component/component.ext', all=True)
            mock_helio_finder.asert_called_with('/javascript', 'path/to/component/component.ext')
            self.assertEqual(static_paths, ['helio/static.js'])

        @patch('helio.heliodjango.finders.exists', return_value=True)
        @patch('helio.heliodjango.finders.helio_static_path', return_value='helio/static.js')
        def test_helio_staticdirs_get(self, mock_helio_finder, mock_exists):
            """When helio_static_dirs is defined, should return from the helio_static_dirs first."""
            self.finder.helio_static_dirs = ['/javascript']
            self.finder.component_base_directories = []
            static_path = self.finder.find('path/to/component/component.ext')
            mock_helio_finder.asert_called_with('/javascript', 'path/to/component/component.ext')
            self.assertEqual(static_path, 'helio/static.js')

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
            """A standard regex (i.e. not a wildcard string prentending to be a regex) should be compiled without
            change."""
            self.finder.component_base_directories = ()
            for _ in self.finder.list(['normal regex.*with middle']):  # generators gonna generate
                pass
            mock_re_compile.assert_called_with('normal regex.*with middle')

        @patch('helio.heliodjango.finders.walk', return_value=(
            ('component/static', [], []),
            ('component2', [], []))
        )
        def test_walk_component_base_dir(self, mock_walk):
            """walk_component_base_dir walks the given directory, returning only 'static' directories and their
            children."""
            static_dirs = [static_dir for static_dir in walk_component_base_dir('mock')]
            self.assertEqual(len(static_dirs), 1)
            self.assertEqual(static_dirs[0][0], 'component/static')

        @patch('helio.heliodjango.finders.walk_component_base_dir', return_value=(
            ('/component_name/static/', [], ('file.js',)),
            ('/component_name/sub_component/', [], ('anotherfile.ext',)),
            ('/component_name/sub_component/static/', [], ('file2.js', 'file3.css', 'ignore.me')))
        )
        @patch('helio.heliodjango.finders.listdir', return_value=[])
        def test_component_static_list(self, mock_helio_finder, mock_walk):
            """The list function should skip directories that aren't 'static' dirs, and files that match the ignore
            list."""
            self.finder.component_base_directories = ('MOCK_BASE_DIR',)
            static_files = [static_file for static_file in self.finder.list(['^ignore'])]
            self.assertEqual(len(static_files), 3)

            self.assertEqual(static_files[0][1].location, '/component_name/static')
            self.assertEqual(static_files[1][1].location, '/component_name/sub_component/static')
            self.assertEqual(static_files[2][1].location, '/component_name/sub_component/static')

            self.assertEqual(static_files[0][0], 'file.js')
            self.assertEqual(static_files[1][0], 'file2.js')
            self.assertEqual(static_files[2][0], 'file3.css')

        @patch('helio.heliodjango.finders.exists', return_value=True)
        @patch('helio.heliodjango.finders.join', return_value='path/to/file.js')
        @patch('helio.heliodjango.finders.isdir', return_value=False)
        def test_helio_static_path_get(self, mock_is_dir, mock_join, mock_exists):
            """helio_static_path should join the helio static path to the file name and return it if it exists."""
            joined_name = helio_static_path('helio_dir', 'filename')
            mock_join.assert_called_with('helio_dir', 'filename')
            mock_is_dir.assert_called_with(joined_name)
            mock_exists.assert_called_with(joined_name)
            self.assertEqual(joined_name, 'path/to/file.js')

        @patch('helio.heliodjango.finders.exists', return_value=False)
        @patch('helio.heliodjango.finders.join', return_value='path/to/file.js')
        def test_helio_static_path_nonexistent_get(self, mock_join, mock_exists):
            """helio_static_path should join the helio static path to the file name and return None if it doesn't
            exist."""
            joined_name = helio_static_path('helio_dir', 'filename')
            mock_join.assert_called_with('helio_dir', 'filename')
            mock_exists.assert_called_with('path/to/file.js')
            self.assertIsNone(joined_name)

        @patch('helio.heliodjango.finders.exists', return_value=True)
        @patch('helio.heliodjango.finders.join', return_value='path/to/file.js')
        @patch('helio.heliodjango.finders.isdir', return_value=True)
        def test_helio_static_path_dir_get(self, mock_is_dir, mock_join, mock_exists):
            """helio_static_path should join the helio static path to the file name and return None if it is a dir."""
            joined_name = helio_static_path('helio_dir', 'filename')
            mock_join.assert_called_with('helio_dir', 'filename')
            mock_is_dir.assert_called_with('path/to/file.js')
            mock_exists.assert_called_with('path/to/file.js')
            self.assertIsNone(joined_name)

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

    class RendererTests(unittest.TestCase):
        @patch.object(RequestContext, '__init__', return_value=None)
        def test_request_context_create(self, mock_rc_init):
            """request_context method should create a new RequestContext from the request"""
            mock_request = MagicMock()
            rc = get_request_context(mock_request)
            mock_rc_init.assert_called_with(mock_request)
            self.assertIsInstance(rc, RequestContext)

        @patch('helio.heliodjango.renderers.render_to_string')
        def test_render_call_with_request(self, mock_render):
            """Render function calls the render_to_string shortcut with the RequestContext if a request is supplied."""
            mock_rc = MagicMock()
            with patch('helio.heliodjango.renderers.get_request_context', return_value=mock_rc) as mock_rc_init:
                context = MagicMock()
                request = MagicMock()
                render('template_name.html', context, request)
                mock_rc_init.assert_called_with(request)
                mock_render.assert_called_with('template_name.html', context, context_instance=mock_rc)

        @patch('helio.heliodjango.renderers.render_to_string')
        def test_render_call_without_request(self, mock_render):
            """Render function calls render_to_string shortcut with just the template and context if no request
            given."""
            context = MagicMock()
            render('template_name.html', context)
            mock_render.assert_called_with('template_name.html', context)

    class MiddlewareTests(unittest.TestCase):
        @patch('helio.heliodjango.middleware.settings.CSRF_COOKIE_NAME', 'csrftoken')
        @patch('helio.heliodjango.middleware.csrf', return_value={'csrf_token': 'csrf-token'})
        def test_csrf_inject(self, mock_csrf):
            """Normally the CSRF value will be set on a response."""
            mw = CSRFHeaderInject()
            request = MagicMock()
            response = MagicMock()
            mw.process_response(request, response)
            response.set_cookie.assert_called_with('csrftoken', 'csrf-token', max_age=31449600)

        @patch('helio.heliodjango.middleware.settings.CSRF_COOKIE_NAME', 'csrftoken')
        @patch('helio.heliodjango.middleware.csrf', return_value={'csrf_token': 'NOTPROVIDED'})
        def test_csrf_no_inject(self, mock_csrf):
            """If CSRF token is 'NOTPROVIDED' it will not be set on the response."""
            mw = CSRFHeaderInject()
            request = MagicMock()
            response = MagicMock()
            mw.process_response(request, response)
            response.set_cookie.assert_not_called()


except ImportError:
    print "Not testing Django integration."
