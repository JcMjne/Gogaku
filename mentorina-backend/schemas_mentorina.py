from pydantic import BaseModel
from typing import List, Optional

# User models
class UserCreate(BaseModel):
  email: str
  password: str
  ui_language: str

class TokenResponse(BaseModel):
  access_token: str
  token_type: str = "bearer"

class UserInfo(BaseModel):
  email: str

class SystemSettings(BaseModel):
  ui_language: str
  gemini_api_key: str

class LanguageSettings(BaseModel):
  language: str
  level: str
  region: str
  gender: str
  speaker_name: str
  request: str = ""

class UpdateVocabularyRequest(BaseModel):
  language: str
  learning_language_idx: str
  known_words: List[str]
  unknown_words: List[str]

class AddVocabularyRequest(BaseModel):
  language: str
  words: List[str]

class GetLangCongigRequest(BaseModel):
  language: str

class GetPageRequest(BaseModel):
  learning_language_idx: int