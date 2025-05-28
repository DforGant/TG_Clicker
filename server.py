from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import User, SessionLog, SessionLocal
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Заменить на наш домен
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# Инициализация БД
@app.on_event("startup")
def on_startup():
    init_db()

# Получени сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Активные сессии
active_sessions = {}

@app.get("/user/{telegram_id}")
def get_user(telegram_id: int):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        user = User(telegram_id=telegram_id)
        db.add(user)
        db.commit()
        db.refresh(user)
    return {"telegram_id": user.telegram_id, "total_clicks": user.total_clicks}

@app.websocket("/ws/{telegram_id}")
async def websocket_endpoint(websocket: WebSocket, telegram_id: int):
    await websocket.accept()

    # Если у пользователя есть активная сессия — закрываем её
    if telegram_id in active_sessions:
        await active_sessions[telegram_id].send_json({"type": "update", "status": "closed"})
        await active_sessions[telegram_id].close()
    
    active_sessions[telegram_id] = websocket
    
    db = SessionLocal()
    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "click":
                user = db.query(User).filter(User.telegram_id == telegram_id).first()
                if not user:
                    user = User(telegram_id=telegram_id)
                    db.add(user)
                user.total_clicks = data["count"]
                db.commit()
    except Exception as e:
        print(f"Сессия закрыта: {e}")
        del active_sessions[telegram_id]
        db.close()

# Для тестирования
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
