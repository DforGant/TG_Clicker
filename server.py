from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sqlite3

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Инициализация БД
conn = sqlite3.connect('clicker.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        telegram_id INTEGER UNIQUE,
        total_clicks INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        start_time DATETIME,
        end_time DATETIME,
        clicks INTEGER
    )
''')

conn.commit()

# Активные сессии
active_sessions = {}

@app.get("/user/{telegram_id}")
def get_user(telegram_id: int):
    cursor.execute("SELECT telegram_id, total_clicks FROM users WHERE telegram_id=?", (telegram_id,))
    user = cursor.fetchone()
    if not user:
        cursor.execute("INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,))
        conn.commit()
        return {"telegram_id": telegram_id, "total_clicks": 0}
    return {"telegram_id": user[0], "total_clicks": user[1]}

@app.websocket("/ws/{telegram_id}")
async def websocket_endpoint(websocket: WebSocket, telegram_id: int):
    await websocket.accept()

    # Если у пользователя есть активная сессия — закрываем её
    if telegram_id in active_sessions:
        await active_sessions[telegram_id].send_json({"type": "update", "status": "closed"})
        await active_sessions[telegram_id].close()
    
    active_sessions[telegram_id] = websocket

    try:
        while True:
            data = await websocket.receive_json()
            if data["type"] == "click":
                cursor.execute("UPDATE users SET total_clicks = ? WHERE telegram_id = ?", (data["count"], telegram_id))
                conn.commit()
    except Exception as e:
        print(f"Сессия закрыта: {e}")
        del active_sessions[telegram_id]

# Для тестирования
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
