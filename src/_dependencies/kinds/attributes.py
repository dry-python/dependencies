from _dependencies.markers import injectable


class _Attributes:
    def __init__(self, origin, attrs):
        self.origin = origin
        self.attrs = attrs


def _is_attributes(name, dependency):
    return isinstance(dependency, _Attributes)


def _make_attributes_spec(dependency):
    origin_spec = yield dependency.origin
    return (
        injectable,
        _AttributesSpec(origin_spec.factory, dependency.attrs),
        origin_spec.args,
        origin_spec.required,
        origin_spec.optional,
    )


class _AttributesSpec:
    def __init__(self, factory, attrs):
        self.factory = factory
        self.attrs = attrs

    def __call__(self, **kwargs):
        __tracebackhide__ = True
        result = self.factory(**kwargs)
        for attr in self.attrs:
            result = getattr(result, attr)
        return result

    @property
    def __name__(self):
        return self.factory.__name__

    @property
    def __dependencies__(self):
        return self.factory.__dependencies__
