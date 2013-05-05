def validate_path(path):
    split_path = path.split('.')

    if '' in split_path:
        raise ValueError("Path may not contain empty components.")

    if split_path[0] != 'page':
        raise ValueError("The root component must be 'page'")


class ViewState(object):
    def __init__(self, root_controller):
        self.root_controller = root_controller
        root_controller.make_root(self)

