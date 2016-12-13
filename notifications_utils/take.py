from notifications_utils.field import Field


class Take():

    def __init__(self, thing):
        self.thing = thing

    @classmethod
    def from_field(cls, field):
        return cls(str(field))

    @classmethod
    def as_field(cls, content, values):
        return cls.from_field(Field(content, values))

    def then(self, func, *args, **kwargs):
        return self.__class__(func(self.thing, *args, **kwargs))

    @property
    def as_string(self):
        return str(self.thing)
