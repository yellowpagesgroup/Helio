from controller.helpers import init_component


def split_and_validate_path(path):
    split_path = path.split('.')

    if '' in split_path:
        raise ValueError("Path may not contain empty components.")

    if split_path[0] != 'page':
        raise ValueError("The root component must be 'page'")

    return split_path


class ViewState(object):
    def __init__(self, root_controller):
        self.root_controller = root_controller
        root_controller.make_root(self)

    def component_from_path(self, path):
        split_path = split_and_validate_path(path)

        if path == 'page':
            return self.root_controller

        component = self.root_controller

        for path_component in split_path[1:]:
            component = component.get_named_child(path_component)

        return component

    def _add_component_to_parent(self, parent_component, component, child_key, is_push):
        if is_push:
            parent_component.push_named_child(child_key, component)
        else:
            parent_component.set_named_child(child_key, component)

    def _parent_component_and_child_key_from_path(self, path):
        split_path = split_and_validate_path(path)

        if len(split_path) < 2:
            raise ValueError('To retrieve a parent component portion, path must have at least two components.')

        parent_component = self.component_from_path('.'.join(split_path[:-1]))
        return parent_component, split_path[-1]

    def insert_component(self, path, component):
        """
        Inserts an already initialised component at the given path.
        Will replace the stack of components already at the path, with a new stack,
        containing just this component.
        """
        parent_component, child_key = self._parent_component_and_child_key_from_path(path)
        self._add_component_to_parent(parent_component, component, child_key, False)

    def insert_new_component(self, path, component_name, *args, **kwargs):
        """
        Similar to the insert_component method, however it takes a component name
        and arguments and will init the component before inserting it at the given path,
        replacing the existing component stack with a new stack containing just this
        component.
        """
        component = init_component(component_name, *args, **kwargs)
        self.insert_component(path, component)
        return component