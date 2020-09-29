from weakref import ref

from _dependencies.markers import injectable
from _dependencies.markers import nested_injector


class _InjectorTypeType(type):
    pass


def _is_nested_injector(name, dependency):
    return isinstance(dependency, _InjectorTypeType)


def _make_nested_injector_spec(dependency):
    return (
        nested_injector,
        _NestedInjectorSpec(dependency),
        {"__self__": False},
        {"__self__"},
        set(),
    )


class _NestedInjectorSpec:
    def __init__(self, injector):
        self.injector = injector

    def __call__(self, __self__):
        parent = injectable, ref(__self__), {}, set(), set()
        subclass = type(self.injector.__name__, (self.injector,), _NonEmptyNamespace())
        subclass.__dependencies__.specs["__parent__"] = parent
        return subclass

    @property
    def __dependencies__(self):
        return self.injector.__dependencies__


class _NonEmptyNamespace(dict):
    def __bool__(self):
        return True
