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



if __name__ == '__main__':
    unittest.main()
