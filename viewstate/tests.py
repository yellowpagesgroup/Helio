import unittest
from mock import MagicMock, patch
from viewstate import ViewState, split_and_validate_path
from controller.base import BaseViewController


class TestViewStateFunctions(unittest.TestCase):
    def test_path_with_invalid_root(self):
        """ValueError is raised when validating a path that doesn't start with 'page.'"""
        self.assertRaises(ValueError, split_and_validate_path, 'component.child-component')

    def test_path_with_blank_compoents(self):
        """ValueError is raised when validating a path that has blank components (i.e. '..' in the path)"""
        self.assertRaises(ValueError, split_and_validate_path, 'page.component..child-component')

    def test_path_split(self):
        self.assertEqual(split_and_validate_path('page.test.path.one.two.three'),
                         (['page', 'test', 'path', 'one', 'two', 'three']))


class TestViewStateClass(unittest.TestCase):
    def setUp(self):
        self.root_controller = BaseViewController()
        self.child_one = BaseViewController()
        self.child_two = BaseViewController()
        self.child_three = BaseViewController()

        self.vs = ViewState(self.root_controller)
        self.root_controller.set_named_child('one', self.child_one)
        self.child_one.set_named_child('two', self.child_two)
        self.child_two.set_named_child('three', self.child_three)

    def test_view_state_init(self):
        """A ViewState can only be inited with a root controller arg."""
        with self.assertRaises(TypeError):
            ViewState()

    def test_root_view_set(self):
        """Initing the ViewState sets the root controller to the root_controller attribute."""
        root_controller = MagicMock()
        vs = ViewState(root_controller)
        self.assertEqual(vs.root_controller, root_controller)

    def test_component_path_retrieval(self):
        """A component can be retrieved from the tree by its path."""
        self.assertEqual(self.vs.component_from_path('page'), self.root_controller)
        self.assertEqual(self.vs.component_from_path('page.one'), self.child_one)
        self.assertEqual(self.vs.component_from_path('page.one.two'), self.child_two)
        self.assertEqual(self.vs.component_from_path('page.one.two.three'), self.child_three)

    def test_root_component_insert_error(self):
        """Inserting a component at path 'page' is invalid and raises a ValueError."""
        new_component = BaseViewController
        self.assertRaises(ValueError, self.vs.insert_component, 'page', new_component)

    def test_component_path_insert(self):
        """A component can be inserted directly using a path, replacing the existing stack there."""
        new_component = BaseViewController()
        self.child_one.set_named_child = MagicMock()
        self.vs.insert_component('page.one.four', new_component)
        self.child_one.set_named_child.assert_called_with('four', new_component)

    def test_new_component_path_insert(self):
        """A new component can be initted (based on component path) and then can be inserted directly using a view path,
        replacing the existing stack there."""
        new_component = MagicMock()
        self.vs.insert_component = MagicMock()
        with patch('viewstate.viewstate.init_component', return_value=new_component) as patched_init:
            self.vs.insert_new_component('page.one.four', 'new.component.path', 'arg1', 'arg2', kwarg1='kwarg1',
                                         kwarg2='kwarg2')
            patched_init.assert_called_with('new.component.path', 'arg1', 'arg2', kwarg1='kwarg1', kwarg2='kwarg2')
            self.vs.insert_component.assert_called_with('page.one.four', new_component)


if __name__ == '__main__':
    unittest.main()