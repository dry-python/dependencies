from _dependencies.checks.circles import _check_circles
from _dependencies.checks.injector import _check_descriptor
from _dependencies.checks.injector import _check_dunder_name
from _dependencies.checks.loops import _check_loops
from _dependencies.spec import _make_dependency_spec


class _Graph:
    def __init__(self, in_class):
        self.in_class = in_class
        self.specs = {}

    def get(self, name):
        return self.specs.get(name)

    def assign(self, name, dependency):
        _check_dunder_name(name)
        _check_descriptor(self.in_class, name, dependency)
        self.specs[name] = _make_dependency_spec(name, dependency)
        _check_circles(self.specs, name)
        _check_loops(self.in_class, self.specs)

    def has(self, name):
        return name in self.specs

    def update(self, graph):
        self.specs.update(graph.specs)
