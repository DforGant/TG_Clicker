from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn

HOST = "127.0.0.1"
PORT = 8000

DataBase = {'users': [],'clicks':{}} # тестовая БД

app = FastAPI() # объект приложения

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

active_connection = {}
dubUser = {}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    print("New connection")
    user = await websocket.receive_text()
    
    if user in active_connection:
        print("dublicateUser")
        dubUser[user] = active_connection[user]
        await dubUser[user].close()
        print(dubUser)

    active_connection[user] = websocket
    clicksUser = 0
    if DataBase['users'].count(user) == 0:
        DataBase['users'].append(user)
        DataBase['clicks'][user] = 0
        
    await websocket.send_text(f"{DataBase['clicks'][user]}")
    
    try:
        while True:
            data = await websocket.receive_text() # получение данных от клиента
            if data =="click":
                clicksUser += 1
                print(clicksUser)
            
    except Exception:
        print("Disconnect")
        if user in dubUser:
            del dubUser[user]
            DataBase['clicks'][user] += clicksUser
            await active_connection[user].send_text(f"{DataBase['clicks'][user]}")
        else:
            DataBase['clicks'][user] += clicksUser
            clicksUser = 0
            del active_connection[user]
        

if __name__ == "__main__":
    uvicorn.run(app, host=HOST, port=PORT) # Запуск Сервера
