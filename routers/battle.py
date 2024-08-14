from fastapi import Depends, HTTPException, APIRouter, WebSocket
from fastapi.security import OAuth2PasswordRequestForm
from controllers.token import get_current_user, create_access_token
from controllers.users import register
from model import schemas
from model.core import User,Battle
from secure import pwd_context
import os
import jwt

SECRET_KEY = os.getenv("SECRET_KEY_JWT")
ALGORITHM = 'HS256'

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
        
    async def append(self, websocket: WebSocket):
        self.active_connections.append(websocket)

    
    async def disconnect(self, websocket: WebSocket,code: int):
        try:
         await websocket.close(code)
         self.active_connections.remove(websocket)
        except Exception:
            pass

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_json(message)


manager = ConnectionManager()


@router.post("/register/", status_code=201)
async def register_user(user_data: schemas.UserCreate):
    return await register(user_data=user_data)


@router.post('/token/', status_code=201)
async def get_token(request: OAuth2PasswordRequestForm = Depends()):
    user = await User.select(ids=[request.username])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid credentials')
    hashpasswdfromdb = await User.select(ids=[request.username],columns=["hashed_password"])
    if not pwd_context.verify(request.password, hashpasswdfromdb[0].get("hashed_password")):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Invalid username or password')

    access_token = create_access_token(data={'username': request.username})

    return {
        'access_token': access_token,
        'token_type': 'bearer',
        'username': request.username,
    }


@router.get("/battle/")
async def battle(current_user: schemas.UserBase = Depends(get_current_user)): 
    if current_user:
        all = await Battle.select()
        return all
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Login please')

@router.websocket("/ws/")
async def websocket_endpoint(websocket: WebSocket):  
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        payload = jwt.decode(data, SECRET_KEY, algorithms=[ALGORITHM])
        decode_username: str = payload.get('username')
        user = await User.select(ids=[decode_username])
        if user:
            await manager.append(websocket)
            await manager.send_personal_message("connect",websocket)
    except Exception:
            await manager.send_personal_message("disconnect",websocket)
            await manager.disconnect(websocket, 1000)
            return



    try:
        while True:
            data = await websocket.receive_json()
            if manager.broadcast:
                pixel = data.get("pixel")
                color = data.get("color")
                if pixel and color is not None:
                    battle = await User.select(ids=[pixel])
                    if battle:
                        await Battle.update(_id=pixel,data={"pixel":pixel,"color":color})
                        await manager.broadcast(data)
                    else:
                        await Battle.insert(Battle(pixel=pixel, color=color))
                        await manager.broadcast(data)
    except Exception:
        await manager.send_personal_message("disconnect",websocket)
        await manager.disconnect(websocket, 1011)
 
