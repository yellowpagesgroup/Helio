import unittest
from mock import patch, MagicMock
from base import BaseViewController, render
from helio.helio_exceptions import UnattachedControllerError
from helio.viewstate.viewstate import ViewState


class TestBaseControllerFunctions(unittest.TestCase):
    def setUp(self):
        self.root = BaseViewController()
        self.view_state = ViewState(self.root)

    def test_set_get_named_child(self):
        """Children can be set and retrieved by name."""
        child = MagicMock()
        bc = BaseViewController()
        bc.set_child('test-child', child)
        retrieved_child = bc.get_child('test-child')
        self.assertEqual(child, retrieved_child)

    def test_root_controller_path(self):
        """ViewState's root controller has the path 'page'."""
        bc = BaseViewController()
        ViewState(bc)
        self.assertEqual(bc.path, 'page')

    def test_root_controller_parent_retrieval(self):
        """The root controller's parent is None."""
        bc = BaseViewController()
        ViewState(bc)
        self.assertIsNone(bc.parent)

    def test_is_root_attribute_set(self):
        """Root controller has is_root set to True."""
        self.assertTrue(self.root.is_root)

    def test_unattached_controller_path_raises_error(self):
        """Retrieving the path for an unattached controller raises UnattachedControllerError."""
        bc = BaseViewController()
        with self.assertRaises(UnattachedControllerError):
            bc.path

    def test_child_controller_local_id(self):
        """A controller that is not the root has its local_id set when attached to its parent."""
        parent = BaseViewController()
        child = BaseViewController()
        parent.set_child('child-key', child)
        self.assertEqual(child.local_id, 'child-key')

    def test_child_path_generation(self):
        """Test children paths are generated properly."""
        root = BaseViewController()
        child = BaseViewController()
        ViewState(root)
        root.set_child('child-key', child)
        self.assertEqual(child.path, 'page.child-key')

    def test_child_post_attach_call(self):
        """Child's post_attach method is called after it is attached to a parent."""
        root = BaseViewController()
        child = BaseViewController()
        child.post_attach = MagicMock()
        root.set_child('child-key', child)
        child.post_attach.assert_called_with()

    def test_child_replacement_event_calls(self):
        """Replacing a child calls the pre_detach and post_detach methods on the final controller in the stack that
        is being replaced."""
        child1 = BaseViewController()
        child1.post_attach = MagicMock()
        child1.pre_detach = MagicMock()
        child1.post_detach = MagicMock()

        child2 = BaseViewController()

        self.root.set_child('child-key', child1)
        child1.post_attach.assert_called_with()
        self.root.set_child('child-key', child2)
        child1.pre_detach.assert_called_with()
        child1.post_detach.assert_called_with()

    def test_view_state_retrieval(self):
        """All controllers in the view hierarchy share the same view_state."""
        child = BaseViewController()
        self.root.set_child('child-key', child)
        self.assertEqual(self.root.view_state, self.view_state)
        self.assertEqual(child.view_state, self.view_state)

    def test_nc_shortcut(self):
        """Test that controller.nc returns the controller's ViewState's NotificationCentre"""
        nc = MagicMock()
        self.view_state.notification_centre = nc
        self.assertEqual(nc, self.root.nc)

    def test_queue_load(self):
        """Test that the queue_load shortcut calls queue_load on the controller's ViewState's NotificationCentre"""
        nc = MagicMock()
        self.view_state.notification_centre = nc
        self.root.queue_load()
        nc.queue_load.assert_called_with(self.root.path, False)
        self.root.queue_load(True)
        nc.queue_load.assert_called_with(self.root.path, True)

    def test_handle_notification(self):
        """Base Controller should implement handle_notification method."""
        self.root.handle_notification('name', 'data', request=None, other_arg=None)

    def test_child_push(self):
        """After pushing a child to a stack, it is then retrievable via child. The previous final controller on
        the stack should have its pre_detach and post_detach methods called."""
        child1 = BaseViewController()
        child1.pre_detach = MagicMock()
        child1.post_detach = MagicMock()

        child2 = BaseViewController()
        child2.post_attach = MagicMock()

        self.root.push_child('child-key', child1)
        self.root.push_child('child-key', child2)
        self.assertEqual(self.root.get_child('child-key'), child2)

        child1.pre_detach.assert_called_with()
        child1.post_detach.assert_called_with()
        child2.post_attach.assert_called_with()

    def test_child_pop(self):
        """After pushing a child to a stack, it can be popped back off."""
        child1 = BaseViewController()
        child2 = BaseViewController()

        child2.post_detach = MagicMock()
        child2.pre_detach = MagicMock()

        self.root.push_child('child-key', child1)
        self.root.push_child('child-key', child2)
        retrieved_child_2 = self.root.pop_child('child-key')
        self.assertEqual(child2, retrieved_child_2)
        child2.pre_detach.assert_called_with()
        child2.post_detach.assert_called_with()
        self.assertEqual(self.root.get_child('child-key'), child1)

    def test_js_id_generation(self):
        """A class' js_id should be None if has_js=False, otherwise it should be js_id property (if set) then
        component_name."""
        self.root.component_name = 'base.component'
        self.root.has_js = False
        self.assertIsNone(self.root.js_id)

        self.root.has_js = True
        self.assertEqual(self.root.js_id, 'base.component')

        self.root.js_id = 'javascript.id'
        self.assertEqual(self.root.js_id, 'javascript.id')

    def test_css_id_generation(self):
        """A class' css_id should be None if has_css=False, otherwise it should be css_id property (if set) then
        component_name."""
        self.root.component_name = 'base.component'
        self.root.has_css = False
        self.assertIsNone(self.root.css_id)

        self.root.has_css = True
        self.assertEqual(self.root.css_id, 'base.component')

        self.root.css_id = 'css.id'
        self.assertEqual(self.root.css_id, 'css.id')

    def test_empty_asset_map(self):
        """A controller should generate an empty asset map if has_js is False and has_css is False."""
        self.root.has_js = False
        self.root.has_css = False

        asset_map = self.root.asset_map()
        self.assertEqual(asset_map, {})

    def test_asset_map_with_js(self):
        """A controller should generate an asset_map with 'script' key to its js_id."""
        self.root.js_id = 'script.id'
        self.root.has_css = False
        asset_map = self.root.asset_map()
        self.assertEqual(asset_map, {'script': 'script.id'})

    def test_asset_map_with_css(self):
        """A controller should generate an asset_map with 'css' key to its css_id."""
        self.root.css_id = 'css.id'
        self.root.has_js = False
        asset_map = self.root.asset_map()
        self.assertEqual(asset_map, {'css': 'css.id'})

    def test_class_map_tree(self):
        """class_map_tree generates a dictionary mapping the paths of every controller down the tree from the starting
        point to the controller's asset_map."""
        child_one = BaseViewController()
        child_one.asset_map = MagicMock(return_value='asset_one')

        child_one_two = BaseViewController()
        child_one_two.asset_map = MagicMock(return_value='asset_one_two')

        child_three = BaseViewController()
        child_three.asset_map = MagicMock(return_value='asset_three')

        child_three_four = BaseViewController()
        child_three_four.asset_map = MagicMock(return_value='asset_three_four')

        self.root.set_child('one', child_one)
        child_one.set_child('two', child_one_two)
        self.root.set_child('three', child_three)
        child_three.set_child('four', child_three_four)

        asset_map_tree = self.root.class_map_tree({})

        self.assertIn('page.one', asset_map_tree)
        self.assertIn('page.one.two', asset_map_tree)
        self.assertIn('page.three', asset_map_tree)
        self.assertIn('page.three.four', asset_map_tree)

        self.assertEqual(asset_map_tree['page.one'], 'asset_one')
        self.assertEqual(asset_map_tree['page.one.two'], 'asset_one_two')
        self.assertEqual(asset_map_tree['page.three'], 'asset_three')
        self.assertEqual(asset_map_tree['page.three.four'], 'asset_three_four')

    def test_template_name_generation(self):
        """Template name should be component_name.html if not set, otherwise it should be whatever was set."""
        self.root.component_name = 'test.component'
        self.assertEqual(self.root.template_name, 'test.component.html')
        self.root.template_name = 'mock-template-name'
        self.assertEqual(self.root.template_name, 'mock-template-name')

    def test_parent_context_get(self):
        """If a controller doesn't have a context, it will take its parent's as a starting point."""
        child_one = BaseViewController()
        self.root.set_child('one', child_one)
        mock_context = MagicMock()
        self.root.context = mock_context
        self.assertEqual(mock_context, child_one.get_context())

    def test_parent_request_get(self):
        """If a controller does not have a request object set, it should get one from its parent."""
        child_one = BaseViewController()
        self.root.set_child('one', child_one)
        mock_request = MagicMock()
        self.root.request = mock_request
        self.assertEqual(mock_request, child_one.get_request())

    def test_passed_request_get(self):
        """If a request is passed into request_get, it should be returned, rather than the controller's request atrr."""
        first_req = MagicMock()
        self.root.request = first_req
        second_req = MagicMock()
        self.assertEqual(self.root.get_request(second_req), second_req)

    @patch('helio.controller.base.render')
    def test_controller_render(self, mock_render):
        """The controller render method should call the standalone render method with the template name, context and
        request. The controller should not replace values in the context with a child if the key already exists."""
        self.root.template_name = 'mock_template.html'
        child_one = BaseViewController()
        self.root.set_child('one', child_one)
        mock_context = {'test': 'mockval', 'one': 'test_one'}
        mock_request = MagicMock()
        self.root.render(mock_context, mock_request)
        mock_render.assert_called_with('mock_template.html', mock_context, mock_request)

    @patch('helio.controller.base.render')
    def test_controller_render_kwargs(self, mock_render):
        """The controller render method should call the standalone render method with the kwargs provided"""
        self.root.template_name = 'mock_template.html'
        child_one = BaseViewController()
        self.root.set_child('one', child_one)
        mock_context = {'test': 'mockval', 'one': 'test_one'}
        mock_request = MagicMock()
        self.root.render(mock_context, mock_request, environment='env', other_arg='arg')
        mock_render.assert_called_with('mock_template.html', mock_context, mock_request,  environment='env',
                                       other_arg='arg')


    @patch('helio.controller.base.render')
    def test_child_controller_context_add(self, mock_render):
        """The controller should insert child components into the context."""
        self.root.template_name = 'mock_template.html'
        child_one = BaseViewController()
        self.root.set_child('one', child_one)
        mock_context = {'test': 'mockval'}
        mock_request = MagicMock()
        self.root.render(mock_context, mock_request)
        mock_render.assert_called_with('mock_template.html', {'test': 'mockval', 'one': child_one}, mock_request)

    @patch('helio.controller.base.TEMPLATE_RENDERER', 'mock.module.render')
    def test_render_wrapper_import_call(self):
        """The render function should be imported based on the TEMPLATE_RENDERER setting, then called with the args &&
        kwargs."""
        mock_render_func = MagicMock()
        mock_module = MagicMock()
        mock_module.render = mock_render_func

        with patch('__builtin__.__import__', return_value=mock_module) as mock_import:
            render('template.html', 'context', 'request', environment='environment', other_arg='other_arg')

            self.assertEqual('mock.module', mock_import.call_args[0][0])
            self.assertEqual('render', mock_import.call_args[0][3])
            mock_module.render.assert_called_with('template.html', 'context', 'request', environment='environment',
                                                  other_arg='other_arg')

    @patch('helio.controller.base.render')
    def test_parent_renderargs_get(self, mock_render):
        """A controller uses its parent's render args as a starting point, updating them with the incoming kwargs before
        passing to the render func."""
        self.root.template_name = 'mock_template.html'
        child_one = BaseViewController()
        child_one.template_name = 'template_name'
        self.root.set_child('one', child_one)
        self.root._render_args = {'parent_arg': 'arg_one'}
        child_one.render({}, 'request', test_arg='an_arg')
        mock_render.assert_called_with('template_name', {}, 'request', parent_arg='arg_one', test_arg='an_arg')

    def test_getstate(self):
        """The controller's __getstate__ method sets request and context to None as these cannot reliably be pickled."""
        self.root.context = 'context'
        self.root.request = 'request'
        serialize_data = self.root.__getstate__()
        self.assertIsNone(serialize_data['request'])
        self.assertIsNone(serialize_data['context'])

    def test_unicode(self):
        """The __unicode__ method should call render with no args."""
        self.root.render = MagicMock()
        self.root.__unicode__()
        self.root.render.assert_called_with()


if __name__ == '__main__':
    unittest.main()
