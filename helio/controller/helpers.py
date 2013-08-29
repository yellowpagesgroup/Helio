from imp import load_source
from os.path import join
from helio.helio_exceptions import ControllerImportError
from helio.settings import COMPONENT_BASE_DIRECTORIES


def get_controller_from_module_path(module_name):
    mod = None

    for path in COMPONENT_BASE_DIRECTORIES:
        mod = None

        module_final = module_name.split('.')[-1]
        controller_path = join(path, module_name.replace('.', '/'), module_final + '.py')
        try:
            mod = load_source(module_final, controller_path)
            break
        except (IOError, ImportError):
            pass

    if mod is not None:
        return mod.Controller
    else:
        raise ControllerImportError(
            "Can't import '%s' controller. Searched in the following directories: %s" % (
                module_name,
                ", ".join(COMPONENT_BASE_DIRECTORIES),
            )
        )


def import_controllers(*args):
    """
    Return either a single controller Class, if one controller name arg is passed,
    or a dictionary of controller Classes, if multiple controller names are passed.
    """
    controllers = {}

    if len(args) == 1:
        return get_controller_from_module_path(args[0])

    for module_name in args:
        controllers[module_name] = get_controller_from_module_path(module_name)

    return controllers


def init_controller(component_name, *args, **kwargs):
    """
    Initialise and return a controller from component_name, with given *args and **kwargs.
    """
    return import_controllers(component_name)(*args, **kwargs)
