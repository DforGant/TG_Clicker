from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import aiosqlite
from pathlib import Path
import datetime

async def create_db():
    async with aiosqlite.connect("clicker.db") as conn:
        # Таблица пользователей
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                total_clicks INTEGER DEFAULT 0
            )
        """)
        # Таблица истории кликов
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS click_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER NOT NULL,
                clicks INTEGER NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        """)
        await conn.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db()
    yield

app = FastAPI(lifespan=lifespan)

active_sessions = {}

@app.get("/", response_class=HTMLResponse)
async def read_index():
    html_path = Path("static/index.html")  # Или "index.html", если рядом с server.py
    if not html_path.is_file():
        return HTMLResponse(content="<h1>index.html не найден</h1>", status_code=404)
    try:
        content = html_path.read_text(encoding="utf-8")
        return HTMLResponse(content=content)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Ошибка: {e}</h1>", status_code=500)

@app.get("/user/{telegram_id}")
async def get_user(telegram_id: int):
    async with aiosqlite.connect("clicker.db") as conn:
        async with conn.execute(
            "SELECT telegram_id, total_clicks FROM users WHERE telegram_id=?", (telegram_id,)
        ) as cursor:
            user = await cursor.fetchone()
            if not user:
                await conn.execute("INSERT INTO users (telegram_id) VALUES (?)", (telegram_id,))
                await conn.commit()
                return {"telegram_id": telegram_id, "total_clicks": 0}
            return {"telegram_id": user[0], "total_clicks": user[1]}

@app.get("/history/{telegram_id}/{date}")
async def get_history_by_date(telegram_id: int, date: str):
    async with aiosqlite.connect("clicker.db") as conn:
        async with conn.execute(
            "SELECT clicks, date FROM click_history WHERE telegram_id=? AND date=? ORDER BY id ASC",
            (telegram_id, date)
        ) as cursor:
            history = await cursor.fetchall()
            # Преобразуем в список словарей для удобства
            return {"history": [{"clicks": row[0], "date": row[1]} for row in history]}

@app.websocket("/ws/{telegram_id}")
async def websocket_endpoint(websocket: WebSocket, telegram_id: int):
    await websocket.accept()
    if telegram_id in active_sessions:
        try:
            await active_sessions[telegram_id].send_json({"type": "update", "status": "closed"})
            await active_sessions[telegram_id].close()
        except Exception as e:
            print(f"Ошибка закрытия сессии: {e}")
    active_sessions[telegram_id] = websocket

    try:
        # Отправляем текущее количество кликов при подключении
        async with aiosqlite.connect("clicker.db") as conn:
            async with conn.execute(
                "SELECT total_clicks FROM users WHERE telegram_id=?", (telegram_id,)
            ) as cursor:
                user = await cursor.fetchone()
                if user:
                    await websocket.send_json({"header": "clicks", "content": user[0]})
                else:
                    await conn.execute("INSERT INTO users (telegram_id, total_clicks) VALUES (?, 0)", (telegram_id,))
                    await conn.commit()
                    await websocket.send_json({"header": "clicks", "content": 0})

        while True:
            data = await websocket.receive_json()
            if data["type"] == "click":
                count = data["count"]
                today = datetime.date.today().isoformat()
                async with aiosqlite.connect("clicker.db") as conn:
                    # Обновляем общее количество кликов
                    await conn.execute(
                        "UPDATE users SET total_clicks = ? WHERE telegram_id = ?",
                        (count, telegram_id)
                    )
                    # Записываем в историю
                    await conn.execute(
                        "INSERT INTO click_history (telegram_id, clicks, date) VALUES (?, ?, ?)",
                        (telegram_id, count, today)
                    )
                    await conn.commit()
                await websocket.send_json({"header": "clicks", "content": count})
    except WebSocketDisconnect:
        print(f"Сессия закрыта: пользователь {telegram_id} отключился")
    except Exception as e:
        print(f"Ошибка в WebSocket: {e}")
    finally:
        if telegram_id in active_sessions:
            del active_sessions[telegram_id]

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
