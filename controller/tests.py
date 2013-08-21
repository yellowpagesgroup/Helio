import unittest
from mock import MagicMock
from base import BaseViewController
from controller_exceptions import UnattachedControllerError
from viewstate.viewstate import ViewState


class TestBaseControllerFunctions(unittest.TestCase):
    def setUp(self):
        self.root = BaseViewController()
        self.view_state = ViewState(self.root)

    def test_set_get_named_child(self):
        """Children can be set and retrieved by name."""
        child = MagicMock()
        bc = BaseViewController()
        bc.set_named_child('test-child', child)
        retrieved_child = bc.get_named_child('test-child')
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
        parent.set_named_child('child-key', child)
        self.assertEqual(child.local_id, 'child-key')

    def test_named_child_path_generation(self):
        """Test named children paths are generated properly."""
        root = BaseViewController()
        child = BaseViewController()
        ViewState(root)
        root.set_named_child('child-key', child)
        self.assertEqual(child.path, 'page.child-key')

    def test_named_child_post_attach_call(self):
        """Child's post_attach method is called after it is attached to a parent."""
        root = BaseViewController()
        child = BaseViewController()
        child.post_attach = MagicMock()
        root.set_named_child('child-key', child)
        child.post_attach.assert_called_with()

    def test_named_child_replacement_event_calls(self):
        """Replacing a named child calls the pre_detach and post_detach methods on the final controller in the stack that
        is being replaced."""
        child1 = BaseViewController()
        child1.post_attach = MagicMock()
        child1.pre_detach = MagicMock()
        child1.post_detach = MagicMock()

        child2 = BaseViewController()

        self.root.set_named_child('child-key', child1)
        child1.post_attach.assert_called_with()
        self.root.set_named_child('child-key', child2)
        child1.pre_detach.assert_called_with()
        child1.post_detach.assert_called_with()

    def test_view_state_retrieval(self):
        """All controllers in the view hierarchy share the same view_state."""
        child = BaseViewController()
        self.root.set_named_child('child-key', child)
        self.assertEqual(self.root.view_state, self.view_state)
        self.assertEqual(child.view_state, self.view_state)

    def test_named_child_push(self):
        """After pushing a child to a named stack, it is then retrievable via child. The previous final controller on
        the stack should have its pre_detach and post_detach methods called."""
        child1 = BaseViewController()
        child1.pre_detach = MagicMock()
        child1.post_detach = MagicMock()

        child2 = BaseViewController()
        child2.post_attach = MagicMock()

        self.root.push_named_child('child-key', child1)
        self.root.push_named_child('child-key', child2)
        self.assertEqual(self.root.get_named_child('child-key'), child2)

        child1.pre_detach.assert_called_with()
        child1.post_detach.assert_called_with()
        child2.post_attach.assert_called_with()

    def test_named_child_pop(self):
        """After pushing a child to a named stack, it can be popped back off."""
        child1 = BaseViewController()
        child2 = BaseViewController()

        child2.post_detach = MagicMock()
        child2.pre_detach = MagicMock()

        self.root.push_named_child('child-key', child1)
        self.root.push_named_child('child-key', child2)
        retrieved_child_2 = self.root.pop_named_child('child-key')
        self.assertEqual(child2, retrieved_child_2)
        child2.pre_detach.assert_called_with()
        child2.post_detach.assert_called_with()
        self.assertEqual(self.root.get_named_child('child-key'), child1)

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

    def test_asset_map_tree(self):
        """asset_map_tree generates a dictionary mapping the paths of every controller down the tree from the starting
        point to the controller's asset_map."""
        child_one = BaseViewController()
        child_one.asset_map = MagicMock(return_value='asset_one')

        child_one_two = BaseViewController()
        child_one_two.asset_map = MagicMock(return_value='asset_one_two')

        child_three = BaseViewController()
        child_three.asset_map = MagicMock(return_value='asset_three')

        child_three_four = BaseViewController()
        child_three_four.asset_map = MagicMock(return_value='asset_three_four')

        self.root.set_named_child('one', child_one)
        child_one.set_named_child('two', child_one_two)
        self.root.set_named_child('three', child_three)
        child_three.set_named_child('four', child_three_four)

        asset_map_tree = self.root.asset_map_tree({})

        self.assertIn('page.one', asset_map_tree)
        self.assertIn('page.one.two', asset_map_tree)
        self.assertIn('page.three', asset_map_tree)
        self.assertIn('page.three.four', asset_map_tree)

        self.assertEqual(asset_map_tree['page.one'], 'asset_one')
        self.assertEqual(asset_map_tree['page.one.two'], 'asset_one_two')
        self.assertEqual(asset_map_tree['page.three'], 'asset_three')
        self.assertEqual(asset_map_tree['page.three.four'], 'asset_three_four')


if __name__ == '__main__':
    unittest.main()
