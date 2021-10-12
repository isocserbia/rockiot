class Singleton:

    def __init__(self, cls):
        self._cls = cls
        self._instance = None

    def Instance(self):
        if self._instance:
            return self._instance
        else:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `get_instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)