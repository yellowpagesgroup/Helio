import unittest
from mock import MagicMock
from base import BaseViewController
from controller_exceptions import UnattachedControllerError
from viewstate.viewstate import ViewState


class TestBaseControllerFunctions(unittest.TestCase):
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
        """Root component has is_root set to True."""
        root = MagicMock()
        ViewState(root)

        self.assertTrue(root.is_root)

    def test_unattached_component_path_raises_error(self):
        """Retrieving the path for an unattached component raises UnattachedControllerError."""

        bc = BaseViewController()

        with self.assertRaises(UnattachedControllerError):
            bc.path

    def test_child_controller_local_id(self):
        """A component that is not the root has its local_id set when attached to its parent."""
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

    def test_view_state_retrieval(self):
        """All controllers in the view hierarchy share the same view_state."""
        root = BaseViewController()
        child = BaseViewController()

        vs = ViewState(root)
        root.set_named_child('child-key', child)

        self.assertEqual(root.view_state, vs)
        self.assertEqual(child.view_state, vs)


if __name__ == '__main__':
    unittest.main()