from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from models import *
from ClassMessage import *
import uvicorn

HOST = "127.0.0.1"
PORT = 8000

app = FastAPI() # объект приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Заменить на наш домен
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# подключение статических фалов (.css,.img и т.д.)
app.mount("/static",StaticFiles(directory="."),name='static')

# для подключения файлов в html нужно в пути к файлу добавить '/static'
# если путь к файлу "index.css" то нужно указать "/static/index.css"

# Инициализация БД при запуске приложения
init_db()


# Получени сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Активные и дублированные сессии
active_sessions = {}
dubUser = {}


html = None

# Тестовая HTML страница
with open('index.html','r',encoding="utf-8") as file:
    html = file.read()

@app.get("/") # обработка запроса получения страницы сайта
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    db = SessionLocal() # Получение сессии БД
    
    print("New connection")
    telegram_id = await websocket.receive_text() # получение telegram_id

    active_user = db.query(User).filter(User.telegram_id == telegram_id).first() # получение данных из БД
    
    if telegram_id in active_sessions: # проверка на использование пользователем нескольких устройств
        dubUser[telegram_id] = active_sessions[telegram_id]
        # обновление истории кликов
        updateSession = db.query(SessionLog).filter(and_(SessionLog.user_id == telegram_id, SessionLog.start_time == dubUser[telegram_id]['session_start'])).first()
        updateSession.end_time = datetime.datetime.now()
        updateSession.clicks = dubUser[telegram_id]['clicksUser']
        db.commit()
        db.close()
        db = SessionLocal()
        await dubUser[telegram_id]['ws'].close() # закрытие websocket соединения

    
    if active_user is None: # проверка существует ли пользователь в БД
        newUser = User(telegram_id=telegram_id,total_clicks=0) # создание новой записи
        db.add(newUser) # добавление новой записи в запрос
        db.commit()  # Выполнение запроса
        db.refresh(newUser) # Обновление БД
    
    active_user = db.query(User).filter(User.telegram_id == telegram_id).first()

    # Установка сессии 
    sessionUser = SessionLog(user_id=telegram_id, clicks=0)
    db.add(sessionUser)
    db.commit()
    db.refresh(sessionUser)
    sessionUser = db.query(SessionLog).filter(and_(SessionLog.user_id == telegram_id, SessionLog.end_time.is_(None))).first()

    active_sessions[telegram_id] = {"ws": websocket, "session_start": sessionUser.start_time, "clicksUser":0}
    print(active_sessions)
    print(active_sessions[telegram_id])
    print(active_sessions[telegram_id]['session_start'])
    
    print("startSession")
    print(telegram_id,active_user.total_clicks,active_sessions[telegram_id]['session_start'],sessionUser.end_time)

    message = Message("clicks",active_user.total_clicks);
    
    await websocket.send_text(message.to_json()) # отпрака данных пользователю
    
    history = db.query(
        func.date(SessionLog.start_time).label('date'),
        func.sum(SessionLog.clicks).label('total')
        ).filter(SessionLog.user_id == telegram_id).group_by(func.date(SessionLog.start_time)).all()
    
    historyUser = ""
    for date, total in history:
        historyUser += f"<div class='session'>Клики за <span>{date}</span>: {total}<span></span></div>"

    message = Message("history",historyUser)
    
    await websocket.send_text(message.to_json())
    
    try:
        while True:
            data = await websocket.receive_text() # получение данных от клиента
            if data =="click":
                active_sessions[telegram_id]['clicksUser'] += 1
                print(active_sessions[telegram_id]['clicksUser'])
            
    except Exception:
        print("Disconnect")
        if telegram_id in dubUser: # проверка на использование пользователем нескольких устройств
            
            db.close() # Закрытие старой БД
            db = SessionLocal() # Получение новой сессии БД для обновления данных
            
            # обновление кликов
            active_user = db.query(User).filter(User.telegram_id == telegram_id).first()
            active_user.total_clicks += dubUser[telegram_id]['clicksUser']
            
            
            db.commit()
            active_user = db.query(User).filter(User.telegram_id == telegram_id).first()
            print("dubUser")
            print(telegram_id,active_user.total_clicks,dubUser[telegram_id]['clicksUser'])

            
            # отправка данных пользователю
            message = Message("clicks",active_user.total_clicks);
            
            await active_sessions[telegram_id]['ws'].send_text(message.to_json())

            history = db.query(
                func.date(SessionLog.start_time).label('date'),
                func.sum(SessionLog.clicks).label('total')
                ).filter(SessionLog.user_id == telegram_id).group_by(func.date(SessionLog.start_time)).all()
    
            historyUser = ""
            for date, total in history:
                historyUser += f"<div class='session'>Клики за <span>{date}</span>: {total}<span></span></div>"

            message = Message("history",historyUser)
            await active_sessions[telegram_id]['ws'].send_text(message.to_json())

            del dubUser[telegram_id] # Удаление старой сессии
            db.close() # Закрытие новой БД
        else: # Запись кликов в БД при отключении соединения
            db.close() # Закрытие старой БД
            db = SessionLocal() # Получение новой сессии БД для обновления данных

            # обновление кликов
            active_user = db.query(User).filter(User.telegram_id == telegram_id).first()
            active_user.total_clicks += active_sessions[telegram_id]['clicksUser'] 

            #обновление истроии кликов
            updateSession = db.query(SessionLog).filter(and_(SessionLog.user_id == telegram_id, SessionLog.start_time == active_sessions[telegram_id]['session_start'])).first()
            updateSession.end_time = datetime.datetime.now()
            updateSession.clicks = active_sessions[telegram_id]['clicksUser']
            
            db.commit()
            active_user = db.query(User).filter(User.telegram_id == telegram_id).first()
            updateSession = db.query(SessionLog).filter(and_(SessionLog.user_id == telegram_id, SessionLog.start_time == active_sessions[telegram_id]['session_start'])).first()
            print("endSession")
            print(updateSession.start_time, updateSession.user_id, updateSession.end_time, updateSession.clicks)
            print(telegram_id,active_user.total_clicks)
            
            db.close()# Закрытие БД
            del active_sessions[telegram_id] # Удаление сессии
        


if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT) # Запуск Сервера

