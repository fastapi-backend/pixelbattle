
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends, status
from model.core import ModelInterface,User,Battle
from secure import oauth2_schema
from typing import Optional
import jwt
import os

SECRET_KEY = os.getenv("SECRET_KEY_JWT")
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
interface = ModelInterface()




def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(oauth2: str = Depends(oauth2_schema)):
    credentials_exeption = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authneticate': 'Bearer'}
    )

    try:
        payload = jwt.decode(oauth2, SECRET_KEY, algorithms=[ALGORITHM])
        decode_username: str = payload.get('username')

        if decode_username is None:
            raise credentials_exeption

        
        user = await interface.get_model_filter(model=User,filter=decode_username)

        if user is None:
            raise credentials_exeption

        return decode_username

    except Exception:
        raise credentials_exeption