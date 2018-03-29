from notifications_utils.field import Field


class Take(str):

    @classmethod
    def from_field(cls, field):
        return cls(field)

    @classmethod
    def as_field(cls, *args, **kwargs):
        return cls.from_field(Field(*args, **kwargs))

    def then(self, func, *args, **kwargs):
        return self.__class__(func(self, *args, **kwargs))
