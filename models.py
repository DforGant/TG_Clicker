from sqlalchemy import create_engine, Column, Integer, String, DateTime, and_, func
from sqlalchemy.orm import sessionmaker, declarative_base
import os
import datetime

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
    start_time = Column(DateTime, default=datetime.datetime.now)
    end_time = Column(DateTime, nullable=True, default=None)
    clicks = Column(Integer)

# Инициализация БД
def init_db():
    Base.metadata.create_all(bind=engine)