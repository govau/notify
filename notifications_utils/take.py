class Take():

    def __init__(self, thing):
        self.thing = thing

    @classmethod
    def from_field(cls, field):
        return cls(str(field))

    def then(self, func, *args, **kwargs):
        return self.__class__(func(self.thing, *args, **kwargs))

    @property
    def as_string(self):
        return str(self.thing)
