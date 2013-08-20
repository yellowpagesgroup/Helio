import unittest
from mock import MagicMock, patch
from viewstate import ViewState, ViewStateManager, split_and_validate_path, get_default_viewstate
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

    def test_default_viewstate_generator(self):
        """get_default_viewstate should return a ViewState instance."""
        vs = get_default_viewstate()
        self.assertIsInstance(vs, ViewState)


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
        self.assertEqual(self.vs.controller_from_path('page'), self.root_controller)
        self.assertEqual(self.vs.controller_from_path('page.one'), self.child_one)
        self.assertEqual(self.vs.controller_from_path('page.one.two'), self.child_two)
        self.assertEqual(self.vs.controller_from_path('page.one.two.three'), self.child_three)

    def test_root_component_insert_error(self):
        """Inserting a component at path 'page' is invalid and raises a ValueError."""
        new_component = BaseViewController
        self.assertRaises(ValueError, self.vs.insert_controller, 'page', new_component)

    def test_component_path_insert(self):
        """A component can be inserted directly using a path, replacing the existing stack there."""
        new_component = BaseViewController()
        self.child_one.set_named_child = MagicMock()
        self.vs.insert_controller('page.one.four', new_component)
        self.child_one.set_named_child.assert_called_with('four', new_component)

    def test_new_component_path_insert(self):
        """A new controller can be instantiated (based on component name) and then can be inserted directly using a view
        path, replacing the existing stack there."""
        new_component = MagicMock()
        self.vs.insert_controller = MagicMock()
        with patch('viewstate.viewstate.init_controller', return_value=new_component) as patched_init:
            self.vs.insert_new_controller('page.one.four', 'new.component.path', 'arg1', 'arg2', kwarg1='kwarg1',
                                         kwarg2='kwarg2')
            patched_init.assert_called_with('new.component.path', 'arg1', 'arg2', kwarg1='kwarg1', kwarg2='kwarg2')
            self.vs.insert_controller.assert_called_with('page.one.four', new_component)

    def test_component_path_push(self):
        """A component can be pushed onto the stack at a path."""
        new_component = MagicMock()
        self.child_one.push_named_child = MagicMock()
        self.vs.push_controller('page.one.four', new_component)
        self.child_one.push_named_child.assert_called_with('four', new_component)

    def test_new_component_path_push(self):
        """A new controller can be instantiated (based on component name) and then can be pushed directly using a view
        path, onto the stack there."""
        new_component = MagicMock()
        self.vs.push_controller = MagicMock()
        with patch('viewstate.viewstate.init_controller', return_value=new_component) as patched_init:
            self.vs.push_new_controller('page.one.four', 'new.component.path', 'arg1', 'arg2', kwarg1='kwarg1',
                                         kwarg2='kwarg2')
            patched_init.assert_called_with('new.component.path', 'arg1', 'arg2', kwarg1='kwarg1', kwarg2='kwarg2')
            self.vs.push_controller.assert_called_with('page.one.four', new_component)

    def test_component_path_pop(self):
        """A component can be popped from the stack by giving its path to the ViewState."""
        # tree looks like this -> page.one.two.three
        self.child_two.pop_named_child = MagicMock(return_value=self.child_three)
        self.child_one.pop_named_child = MagicMock(return_value=self.child_two)

        child_three = self.vs.pop_controller('page.one.two.three')
        child_two = self.vs.pop_controller('page.one.two')

        self.assertEqual(self.child_three, child_three)
        self.assertEqual(self.child_two, child_two)
        self.child_two.pop_named_child.assert_called_with('three')
        self.child_one.pop_named_child.assert_called_with('two')

    def test_page_pop_fails(self):
        """ValueError is raised when trying to pop the root (page)."""
        self.assertRaises(ValueError, self.vs.pop_controller, 'page')


class TestViewStateManagerClass(unittest.TestCase):
    def test_new_viewstate_generation(self):
        """get_unlinked_view_state should generate a new viewstate when called on a new VSM."""
        mock_viewstate = MagicMock()
        with patch('viewstate.viewstate.get_default_viewstate', return_value=mock_viewstate) as mock_gdv:
            vsm = ViewStateManager()
            vs_index, new_vs = vsm.get_unlinked_view_state()
            self.assertEqual(new_vs, mock_viewstate)
            self.assertFalse(new_vs.linked)
            self.assertEqual(vs_index, 0)

    def test_new_viewstate_linking(self):
        """A new viewstate should have its linked property set to True if link=True on get_unlinked_view_state."""
        mock_viewstate = MagicMock()
        with patch('viewstate.viewstate.get_default_viewstate', return_value=mock_viewstate) as mock_gdv:
            vsm = ViewStateManager()
            vs_index, new_vs = vsm.get_unlinked_view_state(link=True)
            self.assertEqual(new_vs, mock_viewstate)
            self.assertTrue(new_vs.linked)
            self.assertEqual(vs_index, 0)

    def test_viewstate_append_on_link(self):
        """Every call to get_unlinked_view_state with link=True should return a viewstate index one higher than the
        previous call."""
        mock_viewstate = MagicMock()
        with patch('viewstate.viewstate.get_default_viewstate', return_value=mock_viewstate) as mock_gdv:
            vsm = ViewStateManager()
            vs_index, new_vs = vsm.get_unlinked_view_state(link=True)
            self.assertEqual(new_vs, mock_viewstate)
            self.assertTrue(new_vs.linked)
            self.assertEqual(vs_index, 0)
            self.assertEqual(mock_gdv.call_count, 1)
            vs_index, new_vs = vsm.get_unlinked_view_state(link=True)
            self.assertTrue(new_vs.linked)
            self.assertEqual(vs_index, 1)
            self.assertEqual(mock_gdv.call_count, 2)
            vs_index, new_vs = vsm.get_unlinked_view_state(link=True)
            self.assertTrue(new_vs.linked)
            self.assertEqual(vs_index, 2)
            self.assertEqual(mock_gdv.call_count, 3)
            self.assertEqual(len(vsm), 3)

    def test_viewstate_consistent_on_no_link(self):
        """Every call to get_unlinked_view_state should return the same viewstate if it is never linked."""
        mock_viewstate = MagicMock()
        with patch('viewstate.viewstate.get_default_viewstate', return_value=mock_viewstate) as mock_gdv:
            vsm = ViewStateManager()
            vs_index, new_vs = vsm.get_unlinked_view_state()
            self.assertEqual(vs_index, 0)
            vs_index, new_vs = vsm.get_unlinked_view_state()
            self.assertEqual(vs_index, 0)
            self.assertEqual(mock_gdv.call_count, 1)
            self.assertEqual(len(vsm), 1)

    def test_link_view_state(self):
        """Calling 'link_view_state' should set the view state's linked property to True."""
        vsm = ViewStateManager()
        vsm.get_unlinked_view_state(link=True)
        vsm.get_unlinked_view_state()

        self.assertEqual(len(vsm), 2)
        self.assertTrue(vsm[0].linked)
        self.assertFalse(vsm[1].linked)

        vsm.link_view_state(1)

        self.assertTrue(vsm[0].linked)
        self.assertTrue(vsm[1].linked)


if __name__ == '__main__':
    unittest.main()