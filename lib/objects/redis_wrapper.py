from redis import StrictRedis
from pickle import dumps, loads
from abc import ABC, abstractmethod


class RedisData(ABC):

    def __init__(self):
        self.redis = StrictRedis(host='redis-models')
        self.data = {}

    @abstractmethod
    def redis_key(self):
        pass

    @abstractmethod
    def initialize(self):
        pass

    def load(self):
        loaded_from_redis = True
        obj = self.redis.get(self.redis_key())
        if not obj:
            self.build()
            obj = self.redis.get(self.redis_key())
            loaded_from_redis = False
        self.data = loads(obj)
        return loaded_from_redis

    def store(self):
        self.redis.set(self.redis_key(), dumps(self.data))

    def build(self):
        self.initialize()
        self.store()

    def has_redis_data(self):
        return self.redis.get(self.redis_key()) is not None

    def __repr__(self):
        return str(self.data)
