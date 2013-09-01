from os.path import join, splitext


def component_template_to_path(template_name):
    split_template_name = template_name.split('/')

    if len(split_template_name) == 1:
        component_name, ext = splitext(split_template_name[-1])
        final_template_name = component_name.split('.')[-1] + ext
    else:
        component_name = split_template_name[0]
        final_template_name = '/'.join(split_template_name[1:])

    component_dir = component_name.replace('.', '/')

    return join(component_dir, final_template_name)