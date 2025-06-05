from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
import uvicorn
import aiosqlite
from pathlib import Path

app = FastAPI()

active_sessions = {}

# Для index.html — отдельный роут (если он лежит в папке static)
@app.get("/", response_class=HTMLResponse)
async def read_index():
    html_path = Path("static/index.html")  # Или просто "index.html", если он рядом с server.py
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

@app.get("/history/{telegram_id}")
async def get_history(telegram_id: int):
    async with aiosqlite.connect("clicker.db") as conn:
        async with conn.execute(
            "SELECT start_time, end_time, clicks FROM sessions WHERE user_id=?", (telegram_id,)
        ) as cursor:
            sessions = await cursor.fetchall()
            return {"sessions": sessions}

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
        while True:
            data = await websocket.receive_json()
            if data["type"] == "click":
                async with aiosqlite.connect("clicker.db") as conn:
                    await conn.execute(
                        "UPDATE users SET total_clicks = ? WHERE telegram_id = ?",
                        (data["count"], telegram_id)
                    )
                    await conn.commit()
                await websocket.send_json({"header": "clicks", "content": data["count"]})
    except WebSocketDisconnect:
        print(f"Сессия закрыта: пользователь {telegram_id} отключился")
    except Exception as e:
        print(f"Ошибка в WebSocket: {e}")
    finally:
        if telegram_id in active_sessions:
            del active_sessions[telegram_id]

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
