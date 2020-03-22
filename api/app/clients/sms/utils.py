import functools
from monotonic import monotonic


def timed(description):
    def decorator(fn):
        @functools.wraps(fn)
        def inner(self, *args, **kwargs):
            start_time = monotonic()
            result = fn(self, *args, **kwargs)
            elapsed_time = monotonic() - start_time
            self.logger.info(f"{description} finished in {elapsed_time}")
            return result

        return inner
    return decorator
