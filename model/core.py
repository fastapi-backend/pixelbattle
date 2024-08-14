import asyncio
from pydantic_redis.asyncio import Model, Store, RedisConfig

class User(Model):
    _primary_key_field: str = 'email'
    email: str
    hashed_password: str
    is_active: bool = True

class Battle(Model):
    _primary_key_field: str = 'pixel'
    pixel: str
    color: str


store = Store(name='db', redis_config=RedisConfig(host='localhost', port=4722))
store.register_model(User)
store.register_model(Battle)