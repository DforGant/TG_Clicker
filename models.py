from sqlalchemy import create_engine, Column, Integer, String, DateTime, and_, func
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import datetime


folder = "DB"
# создание папки DB если её не существует
if not os.path.exists(folder):
    os.makedirs(folder)

# Подключение к БД
engine = create_engine('sqlite:///./DB/clicker.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель пользователя
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    total_clicks = Column(Integer, default=0)

# Модель сессии
class SessionLog(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    start_time = Column(DateTime, nullable=True, default=None)
    end_time = Column(DateTime, nullable=True, default=None)
    clicks = Column(Integer)

# Инициализация БД
def init_db():
    Base.metadata.create_all(bind=engine)

class DB:
    def __init__(self, database = SessionLocal()):
        self.database = database

    def createUser(self,telegram_id):
        newUser = User(telegram_id=telegram_id,total_clicks=0) # создание новой записи
        self.database.add(newUser) # добавление новой записи в запрос
        self.database.commit()  # Выполнение запроса
        self.database.refresh(newUser) # Обновление БД

    def getUser(self,telegram_id):
        user = self.database.query(User).filter(User.telegram_id == telegram_id).first()
        return user

    def getHistoryUser(self,telegram_id):
        return self.database.query(
        func.date(SessionLog.start_time).label('date'),
        func.sum(SessionLog.clicks).label('total')
        ).filter(SessionLog.user_id == telegram_id).group_by(func.date(SessionLog.start_time)).all()

    def updateDataUser(self,telegram_id,session):
        # обновление кликов
        active_user = self.database.query(User).filter(User.telegram_id == telegram_id).first()
        active_user.total_clicks += session['clicksUser'] 
        self.database.commit()
        self.database.refresh(active_user)

        #обновление истории кликов
        sessionUser = SessionLog(user_id=telegram_id, start_time=session['session_start'], end_time=datetime.datetime.now(), clicks=session['clicksUser'])
        self.database.add(sessionUser)
        self.database.commit()
        self.database.refresh(sessionUser)
        
        
    def getSession(self,telegram_id,start_time):
        return self.database.query(SessionLog).filter(and_(SessionLog.user_id == telegram_id, SessionLog.start_time == start_time)).first()

    def close(self):
        self.database.close()

    def getSessions(self,telegram_id):
        return self.database.query(SessionLog.user_id,SessionLog.start_time,SessionLog.end_time,SessionLog.clicks).filter(SessionLog.user_id == telegram_id).all()

    def isActive(self):
        return self.database.is_active    
