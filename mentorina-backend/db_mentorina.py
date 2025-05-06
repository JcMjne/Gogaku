from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey, DateTime, UniqueConstraint, create_engine, Index
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL=os.getenv('DATABASE_URL')  # local SQLite database
# check_same_thread=False is required for SQLite in a multi-threaded environment
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)

class User(Base):
  __tablename__ = "users"

  idx = Column(Integer, primary_key=True, index=True)
  email = Column(String, unique=True, index=True)
  hashed_password = Column(LargeBinary)
  ui_language = Column(String)
  gemini_api_key = Column(String)
  current_language = Column(String, default="English")
  
class LearningLanguage(Base):
  __tablename__ = "learning_languages"

  idx = Column(Integer, primary_key=True, index=True)
  user_idx = Column(Integer, ForeignKey("users.idx"))
  language = Column(String, index=True)
  level = Column(String)
  region = Column(String)
  gender = Column(String)
  speaker_name = Column(String)
  request = Column(String, default="")

  __table_args__ = (UniqueConstraint('user_idx', 'language', name='uix_user_language'),)

  vocabularies = relationship("Vocabulary", back_populates="learning_language", cascade="all, delete")
  learning_queue = relationship("LearningQueue", back_populates="learning_language", cascade="all, delete")

class Vocabulary(Base):
  __tablename__ = "vocabularies"

  idx = Column(Integer, primary_key=True, index=True)
  word = Column(String, nullable=False)
  proficiency = Column(Integer, default=0)
  next_review = Column(DateTime, default=datetime.now)
  learning_language = relationship("LearningLanguage", back_populates="vocabularies")
  learning_language_idx = Column(Integer, ForeignKey("learning_languages.idx"))

  __table_args__ = (Index("proficiency", "next_review"),)

class LearningQueue(Base):
  __tablename__ = "learning_queue"

  idx = Column(Integer, primary_key=True, index=True)
  learning_language = relationship("LearningLanguage", back_populates="learning_queue")
  learning_language_idx = Column(Integer, ForeignKey("learning_languages.idx"))
  sentence = Column(String, nullable=False)
  translation = Column(String, nullable=False)
  explanation = Column(String, nullable=False)

def get_db():
  db=SessionLocal()
  try:
    yield db
  finally:
    db.close()
