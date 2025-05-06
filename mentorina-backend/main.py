#TODO: async database access

from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, HTTPException, Depends, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from pathlib import Path
import sys
import os
import json
import random
import google.auth
import google.auth.transport.requests
from threading import Lock
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from authenticate_mentorina import *
from schemas_mentorina import *
import db_mentorina
from db_mentorina import get_db, User, LearningLanguage, Vocabulary, LearningQueue
import setup_nlp
from google_mentorina import get_audio, get_text, get_due_vocabulary, build_prompts
from dependencies import get_current_user
from vocabulary import get_first_words,convert_word,get_review_interval_unknown,get_review_interval_known

logging.basicConfig(level=logging.DEBUG)
router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
with open(Path(__file__).parent/"data"/"table_lang.json", "r") as f:
  TABLE_LANG_CODE=json.load(f)
with open(Path(__file__).parent/"data"/"ui_lang.json", "r") as f:
  UI_LANG_CODE=json.load(f)

NLPS=setup_nlp.get_nlps()

load_dotenv()
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GCL_PROJECT_ID=os.getenv("GCL_PROJECT_ID")
GEMINI_MODEL=os.getenv("GEMINI_MODEL")
NUM_WORDS_LOAD=int(os.getenv("NUM_WORDS_LOAD"))
MAX_SCORE=int(os.getenv('MAX_SCORE'))

CREDENTIALS, your_project_id = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
AUTH_REQ = google.auth.transport.requests.Request()

def get_access_token():
  if CREDENTIALS.valid:
    return CREDENTIALS.token
  # Lock to ensure thread safety
  with Lock():
    # Check if the token is still valid
    if not CREDENTIALS.valid:
      CREDENTIALS.refresh(AUTH_REQ)
    return CREDENTIALS.token

# FastAPI app with Gemini initialization
@asynccontextmanager
async def lifespan(app: FastAPI):
  # check_same_thread=False is required for SQLite in a multi-threaded environment
  db_mentorina.Base.metadata.create_all(bind=db_mentorina.engine)
  yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],  # Allow all origins (you can specify a list of allowed origins)
  allow_credentials=True,
  allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
  allow_headers=["*"],  # Allow all headers
)
@app.post("/system-settings")
async def save_system_settings(settings: SystemSettings, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
  logging.debug(f"Received token: {token}")
  try:
    email = verify_jwt_token(token) # Check if the token is valid and extract the email
    logging.debug(f"Token valid, user email: {email}")
  except Exception as e:
    logging.error(f"Token validation failed: {e}")
    raise HTTPException(status_code=401, detail="Invalid token")
  
  try:
    user = db.query(User).filter(User.email == email).first()
    if not user:
      raise HTTPException(status_code=404, detail="User not found")
    user.ui_language = settings.ui_language
    user.gemini_api_key = settings.gemini_api_key
    db.commit() # Save changes to the database
    logging.debug(f"User settings updated: {user.email}")
  except SQLAlchemyError as e:
    logging.error(f"Database error: {e}")
    db.rollback()  # Rollback the transaction in case of error
    raise HTTPException(status_code=500, detail="Database error")
  return {"message": "Settings updated"}

@app.get("/user", response_model=UserInfo)
async def get_user_info(token: str = Depends(oauth2_scheme)):
  email = verify_jwt_token(token)  # Check if the token is valid and extract the email
  if not email:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
  return {"email": email}

@app.post("/signup", response_model=TokenResponse)
async def signup(user: UserCreate,db: Session = Depends(get_db)):
  create_user(user.email, user.password, user.ui_language,db)
  token = create_jwt(user.email)
  return {"access_token": token}

@app.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_db)):
  if authenticate_user(form_data.username, form_data.password,db):
    token = create_jwt(form_data.username)
    return {"access_token": token}
  raise HTTPException(status_code=401, detail="Invalid CREDENTIALS")

@app.post("/set_language_setting")
async def set_language_setting(
    data: LanguageSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now = datetime.now()
    if data.language not in TABLE_LANG_CODE or data.language not in NLPS:
        raise HTTPException(status_code=400, detail="Unsupported language")
    # Check if the user already has a setting for the specified language
    setting = db.query(LearningLanguage).filter_by(user_idx=current_user.idx, language=data.language).first()
    user = db.query(User).filter_by(idx=current_user.idx).first()
    user.current_language = data.language
    try:
      if setting:
        # update existing setting
        setting.level = data.level
        setting.region = data.region
        setting.gender = data.gender
        setting.speaker_name = data.speaker_name
        setting.request = data.request
      else:
        # create new setting
        setting = LearningLanguage(
            user_idx=current_user.idx,
            language=data.language,
            level=data.level,
            region=data.region,
            gender=data.gender,
            speaker_name=data.speaker_name,
            request=data.request
        )
        db.add(setting)
        db.commit()
        db.refresh(setting)
        lang_code=TABLE_LANG_CODE[data.language]['spacy'].split('_')[0]
        first_words = get_first_words(lang_code, NLPS[data.language])
        for word in first_words:
          new_vocab = Vocabulary(
              word=word,
              proficiency=0,
              next_review=now,
              learning_language_idx=setting.idx
          )
          db.add(new_vocab)
      db.commit()
      return {"message": "Language setting saved"}
    except Exception as e:
      db.rollback()
      raise HTTPException(status_code=500, detail="Failed to save settings")


@app.get("/table_lang")
async def get_table_lang():
  return JSONResponse(content=TABLE_LANG_CODE, status_code=200)

@app.get("/get_language_setting") # Get language configuration
async def get_language_setting(
  language: str,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  # Check if the user has a setting for the specified language
  setting = db.query(LearningLanguage).filter_by(user_idx=current_user.idx, language=language).first()
  if not setting:
    config={
      "language": language,
      "level": "",
      "region": "",
      "gender": "",
      "speaker_name": "",
      "request": ""
    }
    return JSONResponse(content=config, status_code=200)
  # Get the configuration for the specified language
  config = {
    "language": language,
    "level": setting.level,
    "region": setting.region,
    "gender": setting.gender,
    "speaker_name": setting.speaker_name,
    "request": setting.request
  }
  return JSONResponse(content=config, status_code=200)

@app.get("/get_current_language")
async def get_current_language(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
  ):
  user=db.query(User).filter_by(idx=current_user.idx).first()
  if not user:
    raise HTTPException(status_code=404, detail="User not found")
  current_language = user.current_language
  if not current_language:
    raise HTTPException(status_code=404, detail="Current language not found")
  return JSONResponse(content={"current_language": current_language}, status_code=200)
  
@app.get("/get_ui_language")
async def get_ui_language(lang_code_original: str):
  available_languages = list(UI_LANG_CODE.values())
  lang_code=lang_code_original or "en"
  lang_code=lang_code.split("-")[0]
  default_language = UI_LANG_CODE.get(lang_code, "English")
  out={
    "available_languages": available_languages,
    "default_language": default_language
  }
  return JSONResponse(content=out, status_code=200)

@app.get("/get_current_language_settings")
async def get_current_language_settings(
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user)
):
  current_language = current_user.current_language
  learning_lang = db.query(LearningLanguage)\
    .filter_by(user_idx=current_user.idx, language=current_language)\
    .first()
  if not learning_lang:
    raise HTTPException(status_code=404, detail="Learning language not found.")
  out={"language":current_language,
       "learning_language_idx":learning_lang.idx,}
  return JSONResponse(content=out, status_code=200)

@app.post("/get_page")
async def get_page(
  payload: GetPageRequest,
  background_tasks: BackgroundTasks,
  db: Session = Depends(get_db),
  current_user: User = Depends(get_current_user),
):
  learning_lang=db.query(LearningLanguage).filter_by(idx=payload.learning_language_idx).first()

  # Add background task for adding pages if needed
  background_tasks.add_task(add_pages_if_needed, current_user, learning_lang, db, payload.learning_language_idx)
  
  # Fetch the page from the queue
  page=db.query(LearningQueue).filter_by(learning_language_idx=payload.learning_language_idx).first()
  if not page:
    page=(await generate_pages(current_user,learning_lang,db,num_pages=1))[0]
  else:
    db.delete(page)
    db.commit()
  print(page)
  #Audio generation
  try:
    access_token = get_access_token()
    audio = await get_audio(page["sentence"].replace('+',''), learning_lang.speaker_name, learning_lang.gender, access_token, GCL_PROJECT_ID)
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error generating audio: {str(e)}")
  
  out={
    "sentence": page["sentence"],
    "translation": page["translation"],
    "explanation": page["explanation"],
    "audio": audio
  }
  return JSONResponse(content=out, status_code=200)

async def add_pages_if_needed(current_user, learning_lang, db: Session, learning_language_idx: int):
  # Check the remaining number of pages
  remaining_pages = db.query(LearningQueue).filter_by(learning_language_idx=learning_language_idx).count()
  try:
    # If there are 4 or fewer pages remaining, generate and add 4 new pages
    if remaining_pages <= 4:
      pages=await generate_pages(current_user, learning_lang, db, num_pages=4)
      for page in pages:
        db.add(page)
      db.commit()
  except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=f"Error adding pages: {str(e)}")

async def generate_pages(user: User, learning_lang: LearningLanguage, db: Session, num_pages: int):
  word_and_score = get_due_vocabulary(db,learning_lang.idx)
  word_and_score = random.sample(word_and_score, min(len(word_and_score), NUM_WORDS_LOAD))
  msg = ", ".join([f"{w}: {MAX_SCORE//2 - s}" for w, s in word_and_score])
  system_prompt,user_prompt = build_prompts(user, learning_lang, msg, num_pages)
  nlp = None
  if learning_lang.language in ['Japanese', 'Chinese']:
    nlp = NLPS.get(learning_lang.language)
  elif learning_lang.language == 'Korean':
    nlp = NLPS.get(learning_lang.language)
  try:
    pages=await get_text(system_prompt, user_prompt, GEMINI_API_KEY, GEMINI_MODEL)
    for page in pages:
      if learning_lang.language in ['Japanese', 'Chinese']:
        doc=nlp(page['sentence'])
        page['sentence']='+'.join([token.text for token in doc])
      elif learning_lang.language == 'Korean':
        doc=nlp(page['sentence'])
        lemmas=[token.lemma_ for token in doc]
        words=[token.text for token in doc]
        for word,lemma in zip(words,lemmas):
          page['sentence']=page['sentence'].replace(word,lemma)
      page['explanation']=f"{page['explanation']}\n{page['notes']}"
    return pages
  except Exception as e:
    db.rollback()
    raise HTTPException(status_code=500, detail=f"Error generating text: {str(e)}")
  
@app.post("/update_vocabulary")
def update_vocabulary(
    payload: UpdateVocabularyRequest,
    db: Session = Depends(get_db)
):
    lang = db.query(LearningLanguage).filter_by(
      learning_language_idx=payload.learning_language_idx
    ).first()

    if not lang:
      raise HTTPException(status_code=404, detail="Learning language not found")

    now = datetime.now()
    known_words=set(convert_word(payload.known_words, NLPS[payload.language]))
    unknown_words=set(convert_word(payload.unknown_words, NLPS[payload.language]))
    known_words=list(known_words-unknown_words)
    unknown_words=list(unknown_words)
    # known words
    for word in known_words:
        vocab = db.query(Vocabulary).filter_by(
            word=word,
            learning_language_idx=lang.idx
        ).first()
        if vocab:
            vocab.proficiency = min(MAX_SCORE, vocab.proficiency + 1)
            vocab.next_review = now + get_review_interval_known(vocab.proficiency)
        else:
            # If the word is not found, add it with a proficiency of 0
            new_vocab = Vocabulary(
                word=word,
                proficiency=MAX_SCORE,
                next_review=now,
                learning_language_idx=lang.idx
            )
            db.add(new_vocab)

    # unknown words
    for word in unknown_words:
        vocab = db.query(Vocabulary).filter_by(
            word=word,
            learning_language_idx=lang.idx
        ).first()
        if vocab:
            vocab.proficiency = max(0, vocab.proficiency - 1)
            vocab.next_review = now + get_review_interval_unknown(vocab.proficiency)
        else:
            # If the word is not found, add it with a proficiency of 0
            new_vocab = Vocabulary(
                word=word,
                proficiency=0,
                next_review=now,
                learning_language_idx=lang.idx
            )
            db.add(new_vocab)

    db.commit()

    return {"message": "Vocabulary updated successfully"}

@app.post("/add_vocabulary")
def add_vocabulary(payload: AddVocabularyRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lang = db.query(LearningLanguage).filter_by(
        user_idx=current_user.idx,
        language=payload.language
    ).first()
    if not lang:
        HTTPException(status_code=404, detail="Learning language not found")
    words=convert_word(payload.words, NLPS[payload.language])
    for word in words:
        vocab = db.query(Vocabulary).filter_by(
            word=word,
            learning_language_idx=lang.idx
        ).first()
        if not vocab:
            new_vocab = Vocabulary(
                word=word,
                proficiency=0,
                next_review=datetime.now(),
                learning_language_idx=lang.idx
            )
            db.add(new_vocab)
    db.commit()
    return {"message": "Words added successfully"}
