from os.path import exists, join, getmtime
from jinja2 import BaseLoader, TemplateNotFound
from helio.controller.finders import component_template_to_path


class ComponentTemplateLoader(BaseLoader):
    def __init__(self, base_directories):
        self.base_dirs = base_directories

    def get_source(self, environment, template):
        for base_dir in self.base_dirs:
            full_path = join(base_dir, component_template_to_path(template))
            print full_path
            if exists(full_path):
                mtime = getmtime(full_path)
                with file(full_path) as f:
                    source = f.read().decode('utf-8')
                    return source, full_path, lambda: mtime == getmtime(full_path)

        raise TemplateNotFound(template)
