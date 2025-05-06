from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
import os
import bcrypt
import jwt
from db_mentorina import User
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# State variables
JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret")
JWT_ALGORITHM = "HS256"

def create_user(email: str, password: str, ui_language: str, db: Session):
  password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
  user = User(email=email, hashed_password=password_hash, ui_language=ui_language)
  try:
    db.add(user)
    db.commit()
    db.refresh(user)
  except IntegrityError:
    db.rollback()
    raise HTTPException(status_code=400, detail="Email already registered")

def authenticate_user(email: str, password: str, db: Session):
  user = db.query(User).filter(email == email).first()
  if user and bcrypt.checkpw(password.encode(), user.hashed_password):
    return True
  return False

def create_jwt(email: str):
  return jwt.encode({"email": email}, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt(token: str):
  try:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload.get("email")
  except jwt.PyJWTError:
    return None
 
def verify_jwt_token(token: str) -> str:
  try:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return payload.get("email")  # Extract the user_id from the token payload
  except jwt.ExpiredSignatureError:
    return None
