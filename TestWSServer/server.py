from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from models import *
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

# Инициализация БД при запуске приложения
init_db()


# Получени сессии БД
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Активные дублированные сессии
active_sessions = {}
dubUser = {}

# Тестовая HTML страница
html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Проверка вебсокета</title>
  <style>
    body{

      display: flex;
      align-items: center;
      justify-content: center;
      width: 100%;
      height: 100vh;
      margin: 0px;
    }
    #container{

      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;

    }
    #clicker{

      display: none;

    }
    #reg{

      display:flex;
      flex-direction:column;
      justify-content: center;
      align-items:center;
      text-align: center;
    }
  </style>
</head>
<body>
  <div id="container">
    <div id='reg'>
      <label>Вход в приложение</label>
      <div>Имя пользователя</div>
      <input type='text' id='nameUser' requred><br>
      <button id='regbtn'>Войти в приложение</button>
      <div id='message'></div>
    </div>
    <div id='clicker'>
        <div id="contClick">
          Клики: <span id="clicks">0</span>
        </div>
        <div id="btnClick">
          <button id="btn">Кликни меня</button>
        </div>
    </div>    
  </div>
  <script>

    var ws = null;

    var clicks = null;

    document.getElementById('regbtn').addEventListener('click',()=>{

      if(document.getElementById('nameUser').value!=""){

        document.getElementById('reg').style.display = "none";

        document.getElementById('clicker').style.display = "block";
      
        var ws = new WebSocket("ws://127.0.0.1:8000/ws");

        ws.onopen = function(e){
          let user = document.getElementById('nameUser').value;
        
          ws.send(`${user}`);        
        }
        ws.onmessage = function(e){

          document.getElementById('clicks').innerHTML = e.data;

        }
        ws.onclose = function(e){

          document.body.innerHTML = "Соедиенеие сброшено";
            
        }

        document.getElementById('btn').addEventListener('click',()=>{

          ws.send('click');
          
          let click = document.getElementById('clicks').innerHTML;

          clicks = Number(click)+1;
          
          document.getElementById('clicks').innerHTML = clicks;
 
        });

      }
      else{

       document.getElementById('message').innerHTML = "Введите имя пользователя";

      }

    });
    
  </script>
</body>
</html>
"""

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
        await dubUser[telegram_id].close() # закрытие websocket соединения

    active_sessions[telegram_id] = websocket
    clicksUser = 0
    
    if active_user is None: # проверка существует ли пользователь в БД
        newUser = User(telegram_id=telegram_id,total_clicks=0) # создание новой записи
        db.add(newUser) # добавление новой записи в запрос
        db.commit()  # Выполнение запроса
        db.refresh(newUser) # Обновление БД
    
    active_user = db.query(User).filter(User.telegram_id == telegram_id).first()
    print(telegram_id,active_user.total_clicks)
    
    await websocket.send_text(f"{active_user.total_clicks}") # отпрака данных пользователю
    
    try:
        while True:
            data = await websocket.receive_text() # получение данных от клиента
            if data =="click":
                clicksUser += 1
                print(clicksUser)
            
    except Exception:
        print("Disconnect")
        if telegram_id in dubUser: # проверка на использование пользователем нескольких устройств
            del dubUser[telegram_id] # Удаление старого websocket соединения
            active_user = db.query(User).filter(User.telegram_id == telegram_id).first()
            active_user.total_clicks += clicksUser # обновление кликов
            db.commit()
            active_user = db.query(User).filter(User.telegram_id == telegram_id).first()
            print(telegram_id,active_user.total_clicks)
            await active_sessions[telegram_id].send_text(f"{active_user.total_clicks}")
        else: # Запись кликов в БД при отключении соединения
            active_user = db.query(User).filter(User.telegram_id == telegram_id).first()
            active_user.total_clicks += clicksUser # обновление кликов
            db.commit()
            active_user = db.query(User).filter(User.telegram_id == telegram_id).first()
            print(telegram_id,active_user.total_clicks)
            del active_sessions[telegram_id] # Удаление websocket соединения
        

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT) # Запуск Сервера
