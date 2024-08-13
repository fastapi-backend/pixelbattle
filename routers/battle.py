from fastapi import Depends, HTTPException, APIRouter, WebSocket
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession as Session
from controllers.token import get_current_user, create_access_token
from controllers.users import register
from model import schemas
from model.core import User, Battle
from model.database import SessionLocal
from secure import pwd_context

router = APIRouter()

# Dependency
async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@router.post("/users/register", status_code=201)
async def register_user(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    return await register(db=db, user_data=user_data)


@router.post('/token/', status_code=201)
async def get_token(request: OAuth2PasswordRequestForm = Depends(),
                    db: Session = Depends(get_db)):
    user: User = await db.scalar(select(User).where(User.email == request.username))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid credentials')
    if not pwd_context.verify(request.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid username or password')

    access_token = create_access_token(data={'username': user.email})

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'username': user.email,
    }


@router.get("/battle/")
async def get_user(db: Session = Depends(get_db), current_user: schemas.UserBase = Depends(get_current_user)): 
    if current_user:
        all = await db.execute(select(Battle))
        return all.scalars().all()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket, db: Session = Depends(get_db)):  
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if manager.broadcast:
                pixel = data.get("pixel")
                color = data.get("color")
                if pixel and color is not None:
                    battle: Battle = await db.scalar(select(Battle).where(Battle.pixel == pixel))
                    if battle:
                        battle.color = color
                        await db.commit()
                        await db.refresh(battle)
                    else:
                        battle = Battle(pixel=pixel)
                        battle.color = color
                        db.add(battle)
                        await db.commit()
                        await db.refresh(battle)
                await manager.broadcast(data)
    except Exception:
        manager.disconnect(websocket)
 
