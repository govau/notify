from flask.ext.redis import FlaskRedis
from flask import current_app


class RedisClient:
    redis_store = FlaskRedis()
    active = False

    def init_app(self, app):
        self.active = app.config.get('REDIS_ENABLED')
        if self.active:
            self.redis_store.init_app(app)

    def set(self, key, value, ex=None, px=None, nx=False, xx=False, raise_exception=False):
        if self.active:
            try:
                self.redis_store.set(key, value, ex, px, nx, xx)
            except Exception as e:
                self.__handle_exception(e, raise_exception)

    def incr(self, key, raise_exception=False):
        if self.active:
            try:
                return self.redis_store.incr(key)
            except Exception as e:
                self.__handle_exception(e, raise_exception)

    def get(self, key, raise_exception=False):
        if self.active:
            try:
                return self.redis_store.get(key)
            except Exception as e:
                self.__handle_exception(e, raise_exception)

        return None

    def decrement_hash_value(self, key, value, raise_exception=False):
        return self.increment_hash_value(key, value, raise_exception, incr_by=-1)

    def increment_hash_value(self, key, value, raise_exception=False, incr_by=1):
        if self.active:
            try:
                return self.redis_store.hincrby(key, value, incr_by)
            except Exception as e:
                self.__handle_exception(e, raise_exception)

    def get_all_from_hash(self, key, raise_exception=False):
        if self.active:
            try:
                return self.redis_store.hgetall(key)
            except Exception as e:
                self.__handle_exception(e, raise_exception)

    def set_hash_and_expire(self, key, values, expire_in_seconds, raise_exception=False):
        if self.active:
            try:
                self.redis_store.hmset(key, values)
                return self.redis_store.expire(key, expire_in_seconds)
            except Exception as e:
                self.__handle_exception(e, raise_exception)

    def __handle_exception(self, e, raise_exception):
        current_app.logger.exception(e)
        if raise_exception:
            raise e
