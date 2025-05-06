from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
import sys
import os
sys.path.append(os.path.dirname(__file__))
from authenticate_mentorina import JWT_SECRET,JWT_ALGORITHM
from db_mentorina import User, get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
  try:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    email = payload.get("email")
    if email is None:
      raise HTTPException(status_code=401, detail="Invalid token")
  except jwt.ExpiredSignatureError:
    raise HTTPException(status_code=401, detail="Invalid token")

  user = db.query(User).filter(User.email == email).first()
  if user is None:
    raise HTTPException(status_code=404, detail="User not found")
  return user
