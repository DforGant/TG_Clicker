from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import User, SessionLog, init_db, DB
from ClassMessage import Message
from settings import settings
import uvicorn
import datetime

HOST = settings.HOST
PORT = settings.PORT

app = FastAPI() # объект приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Заменить на наш домен
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# подключение статических фалов (css,img и т.д.)
app.mount("/static",StaticFiles(directory="."),name='static')

# для подключения файлов в html нужно в пути к файлу добавить '/static'
# если путь к файлу "index.css" то нужно указать "/static/index.css"

# Инициализация БД при запуске приложения
init_db()
db = DB()

# Активные и дублированные сессии
active_sessions = {}
dubUser = {}


@app.get("/") # обработка запроса получения страницы сайта
async def get():
    # Тестовая HTML страница
    with open('index.html','r',encoding="utf-8") as file:
        html = file.read()
        return HTMLResponse(html)


@app.websocket("/ws/{telegram_id}")
async def websocket_endpoint(websocket: WebSocket, telegram_id: int):
    await websocket.accept()
    
    global db
    

    
    active_user = db.getUser(telegram_id) # получение данных о пользователе
    
    if telegram_id in active_sessions: # проверка на использование пользователем нескольких устройств
        dubUser[telegram_id] = active_sessions[telegram_id]
        db.updateDataUser(telegram_id,dubUser[telegram_id])
        await dubUser[telegram_id]['ws'].close() # закрытие websocket соединения
        print(f"Disconnect: {telegram_id}")

    print(f"New connection: {telegram_id}")
    start_time = datetime.datetime.now() # Запоминание времени открытого соединения
    
    if active_user is None: # проверка существует ли пользователь в БД
        db.createUser(telegram_id)
        active_user = db.getUser(telegram_id)

    active_sessions[telegram_id] = {"ws": websocket, "session_start": start_time, "clicksUser":0}
    message = Message("clicks",active_user.total_clicks);
    await active_sessions[telegram_id]['ws'].send_text(message.to_json()) # отпрака данных пользователю
    
    history = db.getHistoryUser(telegram_id)
    historyUser = ""
    
    for date, total in history:
        historyUser += f"<div class='session row bg-light border p-3 text-center'><p>Клики за <span>{date}</span>: <span>{total}</span></p></div>"

    message = Message("history",historyUser)
    await active_sessions[telegram_id]['ws'].send_text(message.to_json())
    
    try:
        while True:
            data = await websocket.receive_text() # получение данных от клиента
            if data == "click":
                active_sessions[telegram_id]['clicksUser'] += 1
            
    except WebSocketDisconnect as error:
        if telegram_id in dubUser: # проверка на использование пользователем нескольких устройств
            del dubUser[telegram_id] # Удаление старого соединения
            
        else: # Запись кликов в БД при отключении соединения
            print(f"Disconnect: {telegram_id}")
            db.updateDataUser(telegram_id,active_sessions[telegram_id])
            del active_sessions[telegram_id] # Удаление сессии
        


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT) # Запуск Сервера

