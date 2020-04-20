from abc import ABC, abstractmethod
from collections.abc import Sequence

from flask import abort


class JSONModel(object):

    ALLOWED_PROPERTIES = set()

    def __init__(self, _dict):
        # in the case of a bad request _dict may be `None`
        self._dict = _dict or {}

    def __bool__(self):
        return self._dict != {}

    def __hash__(self):
        return hash(self.id)

    def __dir__(self):
        return super().__dir__() + list(sorted(self.ALLOWED_PROPERTIES))

    def __eq__(self, other):
        return self.id == other.id

    def __getattribute__(self, attr):
        cls = object.__getattribute__(self, '__class__')

        try:
            return object.__getattribute__(self, attr)
        except AttributeError as e:
            # Re-raise any `AttributeError`s that are not directly on
            # this object because they indicate an underlying exception
            # that we don’t want to swallow
            if str(e) != "'{}' object has no attribute '{}'".format(
                cls.__name__, attr
            ):
                raise e

        if attr in object.__getattribute__(self, 'ALLOWED_PROPERTIES'):
            return object.__getattribute__(self, '_dict')[attr]

        raise AttributeError((
            "'{}' object has no attribute '{}' and '{}' is not a field "
            "in the underlying JSON"
        ).format(
            cls.__name__, attr, attr
        ))

    def _get_by_id(self, things, id):
        try:
            return next(thing for thing in things if thing['id'] == str(id))
        except StopIteration:
            abort(404)


class ModelList(ABC, Sequence):

    @property
    @abstractmethod
    def client():
        pass

    @property
    @abstractmethod
    def model():
        pass

    def __init__(self):
        self.items = self.client()

    def __getitem__(self, index):
        return self.model(self.items[index])

    def __len__(self):
        return len(self.items)

    def __add__(self, other):
        return list(self) + list(other)


class InviteTokenError(Exception):
    pass
