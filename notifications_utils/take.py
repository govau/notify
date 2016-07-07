class Take():

    def __init__(self, thing):
        self.thing = thing

    def then(self, func, *args, **kwargs):
        return self.__class__(func(self.thing, *args, **kwargs))

    @property
    def as_string(self):
        return str(self.thing)
