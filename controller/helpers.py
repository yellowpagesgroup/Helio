from controller_exceptions import ComponentImportError
from settings import COMPONENT_DIRECTORIES


def get_controller_from_module_path(module_name):
    for path in COMPONENT_DIRECTORIES:
        mod = None

        module_final = module_name.split('.')[-1]

        namespace = '%s.%s.%s' % (path, module_name, module_final)
        try:
            mod = __import__(namespace, globals(), locals(), "Controller")
            break
        except ImportError:
            pass

    if mod is not None:
        return mod.Controller
    else:
        raise ComponentImportError(
            "Can't import '%s' component. Searched in the following directories: %s" % (
                module_name,
                ", ".join(COMPONENT_DIRECTORIES),
            )
        )


def import_components(*args):
    """
    Return either a single component Class, if one component name arg is passed,
    or a dictionary of component Classes, if multiple component names are passed.
    """
    components = {}

    if len(args) == 1:
        return get_controller_from_module_path(args[0])

    for module_name in args:
        components[module_name] = get_controller_from_module_path(module_name)

    return components


def init_component(component_name, *args, **kwargs):
    """
    Initialise and return a component from component_name, with given *args and **kwargs.
    """
    return import_components(component_name)(*args, **kwargs)
