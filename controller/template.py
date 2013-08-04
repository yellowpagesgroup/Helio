import os.path
from settings import COMPONENT_DIRECTORIES


class Singleton(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(
                                cls, *args, **kwargs)
        return cls._instance


class BaseTemplateLoader(Singleton):
    def __init__(self):
        self.base_dirs = COMPONENT_DIRECTORIES

    def file_path_for_template(self, template_name, has_extension=True):
        split_template_name = template_name.split('.')
        file_name_offset = -2 if has_extension else -1
        file_name = '.'.join(split_template_name[file_name_offset:]) if has_extension else split_template_name[-1]
        component_path = '/'.join(split_template_name[:file_name_offset])
        relative_path = os.path.join(component_path, file_name)
        for base_dir in self.base_dirs:
            full_path = os.path.join(base_dir, relative_path)
            if os.path.exists(full_path):
                return full_path
        raise IOError('Template %s not found.' % template_name)
