from _dependencies.exceptions import DependencyError
from _dependencies.markers import injectable


def _check_circles(dependencies, origin):

    _check_circles_for(dependencies, origin, origin)


def _check_circles_for(dependencies, attrname, origin):

    try:
        argspec = dependencies[attrname]
    except KeyError:
        return

    if argspec.marker is injectable:
        if origin in argspec.args:
            message = "{0!r} is a circular dependency in the {1!r} constructor"
            raise DependencyError(message.format(origin, argspec.factory.__name__))
        for name in argspec.args:
            _check_circles_for(dependencies, name, origin)
