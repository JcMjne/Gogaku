from fastapi import APIRouter
from datetime import timedelta
import os
from wordfreq import top_n_list
from spacy import Language
from dotenv import load_dotenv

load_dotenv()
MAX_SCORE=int(os.getenv('MAX_SCORE'))

router = APIRouter()

def get_first_words(lang_code:str, nlp: Language, num_words=5000):
  """
  Generate the first num_words words for the new language at the specified level.
  """
  words=top_n_list(lang_code,num_words)
  #extract only words
  words=[words[i] for i in range(len(words)) if (words[i].isalpha() and len(words[i])>1)]
  if lang_code=='zh':
    return words
  else:
    word_processed=convert_word(words, nlp)
  return word_processed

def get_review_interval_known(score: int) -> timedelta:
    intervals = {
        1: timedelta(hours=1),
        2: timedelta(days=1),
        3: timedelta(days=5),
        4: timedelta(days=14),
        5: timedelta(days=30),
        6: timedelta(days=30),
        7: timedelta(days=30),
        8: timedelta(days=30),
        9: timedelta(days=30),
        10: timedelta(days=30),
    }
    return intervals.get(max(1, min(score, 10)), timedelta(days=1))

def get_review_interval_unknown(score: int) -> timedelta:
    intervals = {
        0: timedelta(minutes=3),
        1: timedelta(minutes=30),
        2: timedelta(hours=1),
        3: timedelta(days=1),
        4: timedelta(days=3),
    }
    return intervals.get(max(0, min(score, 4)), timedelta(days=1))

def convert_word(words, nlp: Language):
  """
  Lemmatize words and convert them to their base form.

  words: list<str>
  """
  docs=list(nlp.pipe(words))
  words_analyzed=[[token.lemma_ for token in doc] for doc in docs]
  words_lemma=list(set(' '.join([word.lower().replace('+',' ') for sublist in words_analyzed for word in sublist]).split(' ')))
  return words_lemma


