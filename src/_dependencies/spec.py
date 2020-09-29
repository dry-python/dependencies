from functools import wraps
from inspect import isgeneratorfunction

from _dependencies.kinds.attributes import _is_attributes
from _dependencies.kinds.attributes import _make_attributes_spec
from _dependencies.kinds.classes import _is_class
from _dependencies.kinds.classes import _make_class_spec
from _dependencies.kinds.nested import _is_nested_injector
from _dependencies.kinds.nested import _make_nested_injector_spec
from _dependencies.kinds.operation import _is_operation
from _dependencies.kinds.operation import _make_operation_spec
from _dependencies.kinds.package import _is_package
from _dependencies.kinds.package import _make_package_spec
from _dependencies.kinds.raw import _is_raw
from _dependencies.kinds.raw import _make_raw_spec
from _dependencies.kinds.this import _is_this
from _dependencies.kinds.this import _make_this_spec
from _dependencies.kinds.value import _is_value
from _dependencies.kinds.value import _make_value_spec


def _wraps(factory):
    if isgeneratorfunction(factory):
        return _recursive(factory)
    else:
        return _direct(factory)


def _direct(factory):
    @wraps(factory)
    def wrapper(name, dependency):
        return factory(dependency)

    return wrapper


def _recursive(factory):
    @wraps(factory)
    def wrapper(name, dependency):
        factory_state = factory(dependency)
        while True:
            try:
                next_dependency = next(factory_state)
                next_spec = _make_dependency_spec(name, next_dependency)
                factory_state.send(next_spec)
            except StopIteration as result:
                return result.value

    return wrapper


conditions = (
    (_is_attributes, _wraps(_make_attributes_spec)),
    (_is_nested_injector, _wraps(_make_nested_injector_spec)),
    (_is_class, _wraps(_make_class_spec)),
    (_is_this, _wraps(_make_this_spec)),
    (_is_package, _wraps(_make_package_spec)),
    (_is_operation, _wraps(_make_operation_spec)),
    (_is_value, _wraps(_make_value_spec)),
    (_is_raw, _wraps(_make_raw_spec)),
)


def _make_dependency_spec(name, dependency):
    for condition, factory in conditions:
        if condition(name, dependency):
            return _Spec(*factory(name, dependency))


class _Spec:
    def __init__(self, marker, factory, args, required, optional):
        self.marker = marker
        self.factory = factory
        self.args = args
        self.required = required
        self.optional = optional


# FIXME: Don't require to define `__name__` and `__dependencies__` properties in the
# spec classes.  `_ThisSpec` should be called `_ThisFactory` and be stored inside
# `_Spec` class instance.
