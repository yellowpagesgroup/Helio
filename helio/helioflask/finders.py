from os.path import exists, join, isdir, getmtime
from jinja2 import BaseLoader, TemplateNotFound
from helio.controller.finders import component_template_to_path


def real_file_path(path):
    return path if (exists(path) and not isdir(path)) else None


class ComponentTemplateLoader(BaseLoader):
    def __init__(self, base_directories):
        self.base_dirs = base_directories

    def get_source(self, environment, template):
        for base_dir in self.base_dirs:
            full_path = real_file_path(join(base_dir, component_template_to_path(template)))

            if full_path:
                mtime = getmtime(full_path)
                with file(full_path) as f:
                    source = f.read()#.decode('utf-8')
                    return source, full_path, lambda: mtime == getmtime(full_path)

        raise TemplateNotFound(template)

