from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import User, SessionLog, init_db, DB
from ClassMessage import Message
from settings import settings
import hmac
import hashlib
import json
import urllib.parse
import uvicorn
import datetime
import time

HOST = settings.HOST
PORT = settings.PORT
BOT_TOKEN = settings.BOT_TOKEN

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

def validate_telegram_data(init_data: str) -> bool:

    data_dict = dict(urllib.parse.parse_qsl(init_data, keep_blank_values=True))

    received_hash = data_dict.pop("hash", None)
    if not received_hash:
        print("[LOG] No hash received, validation failed.")
        return False

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(data_dict.items()))

    secret_key = hmac.new(
        key="WebAppData".encode(),
        msg=BOT_TOKEN.encode(),
        digestmod=hashlib.sha256
    ).digest()

    computed_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()

    if computed_hash != received_hash:
        print("[LOG] Hash does not match, validation failed.")
        return False
        
    return True


@app.get("/") # обработка запроса получения страницы сайта
async def get():
    # Тестовая HTML страница
    with open('index.html','r',encoding="utf-8") as file:
        html = file.read()
        return HTMLResponse(html)


@app.websocket("/ws/{telegram_id}")
async def websocket_endpoint(websocket: WebSocket, telegram_id: int):
    await websocket.accept()
    initData = await websocket.receive_json()
    isValidateHash = validate_telegram_data(initData['user']['initData'])    
    
    if not isValidateHash:
        message = Message("NoValidHash","<h1>Хеш не совпадает</h1>")
        await websocket.send_text(message.to_json())
        await websocket.close()
    
    global db
    
    active_user = db.getUser(telegram_id) # получение данных о пользователе
    
    if telegram_id in active_sessions: # проверка на использование пользователем нескольких устройств
        db.updateDataUser(telegram_id,active_sessions[telegram_id]) if active_sessions[telegram_id]['clicksUser']!=0 else None
        await active_sessions[telegram_id]['ws'].close() # закрытие websocket соединения
        print(f"Disconnect: {telegram_id}")

    print(f"New connection: {telegram_id}")
    start_time = datetime.datetime.now() # Запоминание времени открытого соединения
    
    if active_user is None: # проверка существует ли пользователь в БД
        db.createUser(telegram_id)
        active_user = db.getUser(telegram_id)

    active_sessions[telegram_id] = {"ws": websocket, "session_start": start_time, "clicksUser":0}
    message = Message("clicks",active_user.total_clicks);
    await active_sessions[telegram_id]['ws'].send_text(message.to_json()) # отпрака данных пользователю

    # история пользователя за сегодня

    historyToday = db.getHistoryUserToday(telegram_id)
    historyUserToday = f"<div class='session activeSession bg-light border p-2 text-center d-flex justify-content-center align-items-center' style='gap: 9px;'>Клики за время<div><div class='timeStart'>Начало: {active_sessions[telegram_id]['session_start'].strftime('%H:%M:%S')}</div><div class='timeEnd'>Конец: --:--:--</div></div>: <span id='activeClicks'>0</span></div>"
    
    for date, startTime, endTime, clicks in historyToday:
        historyUserToday += f"<div class='session bg-light border p-2 text-center d-flex justify-content-center align-items-center' style='gap: 9px;'>Клики за время<div><div class='timeStart'>Начало: {startTime}</div><div class='timeEnd'>Конец: {endTime}</div></div>: <span>{clicks}</span></div>"

    message = Message("historyToday",historyUserToday)

    await active_sessions[telegram_id]['ws'].send_text(message.to_json())
    
    # история пользователя за всер время
    historyTotal = db.getHistoryUser(telegram_id)
    historyUserTotal = ""
    
    for date, total in historyTotal:
        historyUserTotal += f"<div class='session bg-light border p-2 text-center d-flex justify-content-center align-items-center' style='gap: 9px;'><div>Клики за <span>{date}</span>: <span>{total}</span></div></div>"
    
    message = Message("historyTotal",historyUserTotal)
    await active_sessions[telegram_id]['ws'].send_text(message.to_json())
    
    try:
        while True:
            data = await websocket.receive_text() # получение данных от клиента
            if data == "click":
                active_sessions[telegram_id]['clicksUser'] += 1
            
    except WebSocketDisconnect as error:
        if websocket == active_sessions[telegram_id]['ws']:
            # Запись кликов в БД при отключении соединения
            print(f"Disconnect: {telegram_id}")
            db.updateDataUser(telegram_id,active_sessions[telegram_id]) if active_sessions[telegram_id]['clicksUser']!=0 else None 
            del active_sessions[telegram_id] # Удаление сессии

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT) # Запуск Сервера

