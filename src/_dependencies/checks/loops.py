from _dependencies.exceptions import DependencyError
from _dependencies.markers import injectable
from _dependencies.markers import nested_injector
from _dependencies.markers import this


def _check_loops(class_name, dependencies):

    for attrname, spec in dependencies.items():
        if spec.marker is this:
            _check_loops_for(
                class_name, attrname, dependencies, spec, _filter_expression(spec)
            )
        elif spec.marker is nested_injector:
            _check_loops(class_name, _nested_dependencies(dependencies, spec))


def _check_loops_for(class_name, attribute_name, dependencies, origin, expression):

    try:
        attrname = next(expression)
    except StopIteration:
        return

    try:
        spec = dependencies[attrname]
    except KeyError:
        return

    if spec.marker is nested_injector:
        _check_loops_for(
            class_name,
            attribute_name,
            _nested_dependencies(dependencies, spec),
            origin,
            expression,
        )
    elif attrname == "__parent__":
        from weakref import ReferenceType

        if isinstance(spec.factory, ReferenceType):
            resolved_parent = spec.factory().__dependencies__.specs
        else:
            resolved_parent = spec.factory
        _check_loops_for(
            class_name, attribute_name, resolved_parent, origin, expression
        )
    elif spec is origin:
        message = "{0!r} is a circle link in the {1!r} injector"
        raise DependencyError(message.format(attribute_name, class_name))
    elif spec.marker is this:
        _check_loops_for(
            class_name, attribute_name, dependencies, origin, _filter_expression(spec)
        )


def _filter_expression(spec):

    for kind, symbol in spec.factory.__expression__:
        if kind == ".":
            yield symbol
        elif kind == "[]":
            raise StopIteration()


def _nested_dependencies(parent, spec):

    result = {}
    result.update(spec.factory.__dependencies__.specs)
    result.update({"__parent__": (injectable, parent, {}, set(), set())})
    return result
