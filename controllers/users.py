from fastapi import HTTPException,Depends
from starlette.status import HTTP_400_BAD_REQUEST
from model.core import User
from model.schemas import UserCreate
from secure import pwd_context


async def register(user_data: UserCreate):
    if await User.select(ids=[user_data.email]):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="User with this email already exists!"
        )



    user_hashpasswd = pwd_context.hash(user_data.password)
    await User.insert(User(email=user_data.email, hashed_password=user_hashpasswd))
    return "succes"
