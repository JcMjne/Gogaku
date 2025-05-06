from fastapi import HTTPException
import json
import httpx
import base64
import os
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Tuple
from dotenv import load_dotenv

import sys
sys.path.append(os.path.dirname(__file__))
from db_mentorina import User, LearningLanguage, Vocabulary

load_dotenv()
MAX_SCORE=int(os.getenv('MAX_SCORE'))

async def get_audio(text,speaker_name,gender,access_token,project_id):
  languageCode='-'.join(speaker_name.split('-')[:2])
  url = "https://texttospeech.googleapis.com/v1/text:synthesize"
  headers = {
		"Authorization": f"Bearer {access_token}",
		"x-goog-user-project": project_id,
		"Content-Type": "application/json; charset=utf-8"
  }
  data = {
    "input": {
        "text": text
    },
    "voice": {
      "languageCode": languageCode,
      "name": speaker_name,
      "ssmlGender": gender
    },
    "audioConfig": {
        "audioEncoding": "MP3"
    }
  }
  async with httpx.AsyncClient(timeout=600.0) as client:
    response = await client.post(url, headers=headers, json=data)
  if response.status_code == 200:
    audio_content = response.json().get("audioContent")
    audio_bytes = base64.b64decode(audio_content)
    return audio_bytes
  else:
    raise HTTPException(status_code=response.status_code)
  
async def get_text(system_prompt, user_prompt, gemini_api_key, model):
  url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_api_key}"
  headers = {"Content-Type": "application/json"}
  data = {
     "system_instruction": {
        "parts": [
              {"text": system_prompt}
          ]
      },
      "contents": [
          {
              "parts": [
                  {
                      "text": user_prompt
                  }
              ]
          }
      ],
      "generationConfig": {
          "response_mime_type": "application/json",
          "thinkingConfig": {"thinkingBudget": 0}
      }
  }
  async with httpx.AsyncClient(timeout=600.0) as client:
    response = await client.post(url, headers=headers, json=data)
  if response.status_code == 200:
    result = response.json()
    try:
      text_part = result['candidates'][0]['content']['parts'][0]['text']
      out = json.loads(text_part)
      return out
    except (KeyError, IndexError, json.JSONDecodeError) as e:
      text_part = text_part if 'text_part' in locals() else "N/A"
      raise HTTPException(status_code=500, detail=f"Failed to parse Gemini response: {str(e)}\n{text_part}")
  else:
    raise HTTPException(status_code=response.status_code, detail=response.text)
  
def get_due_vocabulary(db: Session, learning_language_idx: int) -> List[Tuple[str, int]]:
  now = datetime.now()
  return (
    db.query(Vocabulary.word, Vocabulary.proficiency)
    .join(LearningLanguage)
    .filter(Vocabulary.learning_language_idx == learning_language_idx)
    .filter(Vocabulary.proficiency < MAX_SCORE//2)
    .filter(Vocabulary.next_review < now)
    .all()
  )

def build_prompts(user: User, lang: LearningLanguage, msg: str, num_output) -> Tuple[str, str]:
    system = f"You are teaching {lang.language} to {user.ui_language} students at the {lang.level} level."

    user_text = f"""
Here is a list of words followed by their priority scores:
`[{msg}]`

Generate a sentence in {lang.language} at the {lang.level} level. Then, provide its translation and a detailed explanation.

- Translations and explanations must be in {user.ui_language}.
- The explanations should be appropriate for {lang.level}-level students.
- Use **more than 3** words from the list in the sentence.
- Ensure the sentence is grammatically correct, meaningful on its own, and natural.
- You may change the form of words as needed.
- Prioritize words with higher scores when generating the sentence.
- In the Explanation section, describe word conjugations and meanings in list format.
- **Do not refer to the scores or the word list** in the explanation.
- At the end of the Explanation, include grammatical notes relevant to {lang.level}-level learners.
- **Do not include any "+" symbols in the generated sentence.**\
{f"\n\nHere's additional requests from the student:\n{lang.request}" if lang.request else ""}

```
"""+"""
Page = {
"sentence": str,
"translation": str,
"explanation": str,
"notes": str
}
"""+f"""
Return: list[Page*{num_output}]
"""
    return system, user_text