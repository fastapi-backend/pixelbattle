from fastapi import HTTPException,Depends
from sqlalchemy import select
from starlette.status import HTTP_400_BAD_REQUEST
from sqlalchemy.ext.asyncio import AsyncSession as Session
from model.core import User
from model.schemas import UserCreate
from secure import pwd_context
from model.database import SessionLocal
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()

async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if await db.scalar(select(User).where(User.email == user_data.email)):
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="User with this email already exists!"
        )


    user = User(email=user_data.email)
    user.hashed_password = pwd_context.hash(user_data.password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user