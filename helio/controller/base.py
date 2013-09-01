from helio.settings import TEMPLATE_RENDERER
from helio.helio_exceptions import UnattachedControllerError


def render(template_name, context, request, **kwargs):
    split_renderer_module = TEMPLATE_RENDERER.split('.')
    render_function_name = split_renderer_module[-1]
    render_module = __import__('.'.join(split_renderer_module[:-1]), globals(), locals(), split_renderer_module[-1])
    render_func = getattr(render_module, render_function_name)
    return render_func(template_name, context, request, **kwargs)


class BaseViewController(object):
    component_name = None
    has_js = False
    _js_id = None
    has_css = False
    _css_id = None
    _template_name = None

    def __init__(self):
        self._children = {}
        self._view_state = None
        self._render_args = {}
        self.context = None
        self.request = None

        self._local_id = None
        self.parent = None
        self.is_root = False

    def __getstate__(self):
        self.request = None
        self.context = None
        self._render_args = {}
        return self.__dict__

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

    @property
    def nc(self):
        return self.view_state.notification_centre

    def make_root(self, view_state):
        self._view_state = view_state
        self.is_root = True

    def attach(self, parent, local_id):
        self.parent = parent
        self.local_id = local_id

    def set_child(self, child_key, child):
        if child_key in self._children and len(self._children[child_key]):
            replaced_child = self._children[child_key][-1]
            replaced_child._pre_detach()
        else:
            replaced_child = None

        self._children[child_key] = [child]
        child.attach(self, child_key)

        if replaced_child:
            replaced_child._post_detach()

        child._post_attach()

    def get_child(self, child_key):
        return self._children[child_key][-1]

    def push_child(self, child_key, child):
        if not child_key in self._children:
            self._children[child_key] = []
            replaced_child = None
        else:
            replaced_child = self._children[child_key][-1]
            replaced_child._pre_detach()

        self._children[child_key].append(child)
        child.attach(self, child_key)

        if replaced_child:
            replaced_child._post_detach()

        child._post_attach()

    def pop_child(self, child_key):
        final_child = self._children[child_key].pop(-1)
        final_child._pre_detach()
        final_child._post_detach()

        if self._children[child_key]:
            self._children[child_key][-1].attach(self, child_key)
            self._children[child_key][-1]._post_attach()

        return final_child

    def _post_attach(self):
        self.post_attach()

    def _pre_detach(self):
        self.pre_detach()

    def _post_detach(self):
        self.parent = None
        self.post_detach()

    # asset name and map generation

    def asset_map(self):
        asset_map = {}
        if self.js_id:
            asset_map['script'] = self.js_id

        if self.css_id:
            asset_map['css'] = self.css_id

        return asset_map

    def class_map_tree(self, current_tree):
        for child_controller_stack in self._children.itervalues():
            if len(child_controller_stack):
                child_controller_stack[-1].class_map_tree(current_tree)

        current_tree[self.path] = self.asset_map()

        return current_tree

    @property
    def js_id(self):
        if self._js_id:
            return self._js_id

        return self.component_name if self.has_js else None

    @js_id.setter
    def js_id(self, val):
        self._js_id = val

    @property
    def css_id(self):
        if self._css_id:
            return self._css_id

        return self.component_name if self.has_css else None

    @css_id.setter
    def css_id(self, val):
        self._css_id = val

    @property
    def template_name(self):
        if self._template_name:
            return self._template_name
        return self.component_name + '.html'

    @template_name.setter
    def template_name(self, val):
        self._template_name = val

    def get_request(self, request=None):
        if request is None:
            if self.request:
                return self.request

            if self.parent:
                return self.parent.get_request()

        return request

    def _context_insert_children(self):
        for context_var in self._children:
            if not context_var in self.context:
                child = self.get_child(context_var)

                if child is not None:
                    self.context[context_var] = self.get_child(context_var)

    def get_context(self):
        if self.context is None:
            if self.parent:
                self.context = self.parent.get_context()
            else:
                self.context = {}

        return self.context

    def _context_setup(self):
        self.get_context()
        self._context_insert_children()
        self.context_setup()

    def render(self, context=None, request=None, **kwargs):
        self._context_setup()
        if context is not None:
            self.context.update(context)
        self.request = self.get_request(request)
        if self.parent:
            self._render_args = self.parent._render_args

        self._render_args.update(kwargs)

        return render(self.template_name, self.context, self.request, **self._render_args)

    def __unicode__(self):
        return self.render()

    def queue_load(self, scroll_top=False):
        """Shortcut for self.nc.queue_load(self.path)"""
        self.nc.queue_load(self.path, scroll_top)

    # Controllers should override the following methods, as appropriate

    def handle_notification(self, notification_name, data, request=None, **kwargs):
        pass

    def context_setup(self):
        """Set up the render context with variables to go to the template."""
        pass

    def post_attach(self):
        """The controller now has a ViewState (and path) so it should do things here that rely on having them."""
        pass

    def pre_detach(self):
        """The controller is about to be detached from its ViewState, so do things teardown things that can only be
        done while it still has a path e.g. unsubscribe from notifications."""
        pass

    def post_detach(self):
        """Controller has been detached from the ViewState, do any final clean ups here (but nothing that involves
        a path or having access to the ViewState."""
        pass
