def render(template, context, request=None, environment=None):
    if environment is None:
        raise TypeError("Cannot render with no environment provided.")

    template_obj = environment.get_template(template)
    return template_obj.render(request=request, **context)