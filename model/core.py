import asyncio
from pydantic_redis.asyncio import Model, Store, RedisConfig
from typing import Optional,List

class User(Model):
    _primary_key_field: str = 'email'
    email: str
    hashed_password: str
    is_active: bool = True

class Battle(Model):
    _primary_key_field: str = 'pixel'
    pixel: str
    color: str




class ModelInterface:
    def __init__(self):
        store = Store(name='db', redis_config=RedisConfig(host='localhost', port=4722))
        store.register_model(User)
        store.register_model(Battle)


    async def set_user_email_passwd(self,email: str,hashed_password: str):
        await User.insert(User(email=email,hashed_password=hashed_password))


    async def set_battle_pixel_color(self,pixel: str,color: str):
        await Battle.insert(Battle(pixel=pixel,color=color))        


    async def update_model(self,model:str,_id:str,data:str):
        await model.update(_id=_id,data=data)    

    
    async def get_model_filter(self,model:str,filter:str):
        return await model.select(ids=[filter])

        
    async def get_model_filter_column(self,model:str,filter:str,column:str):
        return await model.select(ids=[filter],columns=[column])    


    async def get_model(self,model:str):
        return await model.select()      
 
