class UnattachedControllerError(Exception):
    """Raised if trying to do an operation that does not make sense with a controller that is not yet attached to the
    ViewState hierarchy, e.g. retrieving the controller's path."""