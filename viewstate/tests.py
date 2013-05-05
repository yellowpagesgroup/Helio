import unittest
from mock import MagicMock
from viewstate import ViewState, validate_path


class TestViewStateFunctions(unittest.TestCase):
    def test_path_with_invalid_root(self):
        """ValueError is raised when validating a path that doesn't start with 'page.'"""
        self.assertRaises(ValueError, validate_path, 'component.child-component')

    def test_path_with_blank_compoents(self):
        """ValueError is raised when validating a path that has blank components (i.e. '..' in the path)"""
        self.assertRaises(ValueError, validate_path, 'component..child-component')


class TestViewStateClass(unittest.TestCase):
    def test_view_state_init(self):
        """A ViewState can only be inited with a root controller arg."""

        with self.assertRaises(TypeError):
            ViewState()

    def test_root_view_set(self):
        """Initing the ViewState sets the root controller to the root_controller attribute."""
        root_controller = MagicMock()

        vs = ViewState(root_controller)

        self.assertEqual(vs.root_controller, root_controller)


if __name__ == '__main__':
    unittest.main()