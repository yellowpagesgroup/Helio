from controller_exceptions import UnattachedControllerError


class BaseViewController(object):
    def __init__(self):
        self._named_children = {}
        self._indexed_children = []
        self._view_state = None

        self._local_id = None
        self.parent = None
        self.is_root = False

    @property
    def local_id(self):
        return self._local_id if self._local_id else 'page'

    @local_id.setter
    def local_id(self, new_id):
        self._local_id = new_id

    @property
    def path(self):
        if self.parent:
            return '{0}.{1}'.format(self.parent.path, self.local_id)
        elif self.is_root:
            return self.local_id

        raise UnattachedControllerError("Cannot retrieve a path for an unattached controller.")

    @property
    def view_state(self):
        return self.parent.view_state if self.parent else self._view_state

    def make_root(self, view_state):
        self._view_state = view_state
        self.is_root = True
        self._post_attach()

    def attach(self, parent, local_id):
        self.parent = parent
        self.local_id = local_id

    def set_named_child(self, child_key, child):
        child.attach(self, child_key)
        self._named_children[child_key] = [child]
        child._post_attach()

    def get_named_child(self, child_key):
        return self._named_children[child_key][-1]

    def _post_attach(self):
        self.post_attach()

    # Controllers should override the following methods, as appropriate

    def post_attach(self):
        pass