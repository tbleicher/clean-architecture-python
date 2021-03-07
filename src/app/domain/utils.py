def implements_method(subclass, name):
    return hasattr(subclass, name) and callable(subclass.__dict__[name])


def implements_interface(cls, subclass):
    all_names = cls.__dict__.keys()
    method_names = list(filter(lambda name: not name.startswith("_"), all_names))

    implemented_methods = list(
        map(lambda name: implements_method(subclass, name), method_names)
    )

    return all(list(implemented_methods))
