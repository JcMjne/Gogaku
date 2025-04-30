from gogaku.vocab_manager.vocab_manager import Vocab_Manager
import os,time
from google.genai import types
import streamlit as st
import numpy as np

class Vocab_Manager_Gemini(Vocab_Manager):
  def __init__(self):
    pass
  
  def load_score(self):
    """
    Load the words and their proficiency scores.
    """
    data=np.loadtxt(self.vocab_db_path,delimiter=",",dtype=str,encoding='utf-16').reshape(-1,3)
    self.words=data[:,0]
    self.scores=data[:,1].astype(int)
    self.timestamps=data[:, 2].astype(int)
    current_time=int(time.time())

    #Select words with proficiency score less than self.max_score
    idx_learning=np.where((self.scores<self.max_score)*(self.timestamps<current_time))[0]
    self.word_learning=self.words[idx_learning]
    self.score_leaning=self.scores[idx_learning]
    self.timestamp_learning = self.timestamps[idx_learning]
    msg=[f"{self.word_learning[i]}: {self.max_score-self.score_leaning[i]}, " for i in range(len(idx_learning))]
    self.msg_user=self.msg_user_format.format("".join(msg))

  def save_score(self):
    """
    Save the words and their proficiency scores.
    """
    np.savetxt(self.vocab_db_path,np.column_stack([self.words,self.scores,self.timestamps]),delimiter=",",fmt="%s",encoding='utf-16')

  def generate_sentence(self):
    """
    Generate a sentence using the language model.
    """
    response=st.session_state['gemini_client'].models.generate_content(
      model=st.session_state['param']['current_model'],
      config=types.GenerateContentConfig(
        temperature=st.session_state['param']['gemini_temperature'],
        system_instruction=self.msg_sys,
        thinking_config=types.ThinkingConfig(thinking_budget=0)
        ),
      contents=self.msg_user).text
    self.sentence=response.split('Sentence:')[1].split('Translation:')[0].strip().replace('*','')
    self.translation=response.split('Translation:')[1].split('Explanation:')[0].strip()
    self.explanation=response.split('Explanation:')[1].strip()
    #preprocess additional_words
    if len(st.session_state['additional_words'])!=0:
      doc=st.session_state['nlp'](st.session_state['additional_words'])
      self.new_words=[token.lemma_.lower() for token in doc if token.is_alpha and len(token)>2]
      st.session_state['additional_words']=''
    else:
      self.new_words=[]
    
  def update_setting(self,language,proficiency,request=''):
    self.new_words=[]
    self.language=language
    self.proficiency=proficiency
    self.db_dir=st.session_state['param']['dir_vocab']
    os.makedirs(self.db_dir,exist_ok=True)
    self.vocab_db_path=f'{self.db_dir}{self.language.replace(' ','_').lower()}.csv'
    self.max_score=st.session_state['param']['MAX_SCORE']
    self.msg_sys=f"""You are teaching {self.language} to {st.session_state['param']['user_language']} students at the {self.proficiency} level. \
    Translations and explanations must be done in native level {st.session_state['param']['user_language']}. \
    The content of the explanations should also be suitable for the {self.proficiency} level students."""
              
    self.msg_user_format=f"""
    Here is a list of words followed by their priority scores; """+"""
    {}"""+f"""

    Create a sentence in {self.language} at the {self.proficiency} level.
    You must use more than 3 words from the list in the generated sentence.
    Most importantly, the generated sentence should be grammatically correct, meaningful on its own, and sound natural.
    Change the form of the words if necessary.
    Prioritize higher score words in the list to generate the sentence.
    
    The output must strictly follow this format:
      Sentence:<Generated sentence >
      Translation:<Translation of generated sentence in {st.session_state['param']['user_language']}>
      Explanation:<Detailed grammatical explanation in {st.session_state['param']['user_language']}>
      Notes:\n<Grammatical notes>

    In the Explanation section, describe word conjugations and meanings in list format, but do not mention to the scores and the word list.
    At the end of Explanation, add notes about {self.proficiency} level grammatical tips used in the generated sentence.
    """+request
    self.load_score()

  def convert_word(self,words):
    """
    Convert verb to its base form.
    Convert noun to its singular form.

    words: list<str>
    """
    if self.language in ['Chinese','Korean','Japanese']:
      return words
    docs=list(st.session_state['nlp'].pipe(words))
    words_analyzed=[[token.lemma_ for token in doc] for doc in docs]
    words_lemma=list(set(' '.join([word.lower() for sublist in words_analyzed for word in sublist]).split(' ')))
    return words_lemma
  
  def update_score(self,unfamiliar_words,familiar_words):
    """
    Update the proficiency scores of the words.
    Add words to the database if they are not already present.
    """
    word_dict_score={word:score for word,score in zip(self.words,self.scores)}
    word_dict_timestamp={word:timestamp for word,timestamp in zip(self.words,self.timestamps)}
    if len(unfamiliar_words)!=0:
      unfamiliar_words=self.convert_word(unfamiliar_words)
    if len(familiar_words)!=0:
      familiar_words=self.convert_word(familiar_words)
    familiar_words=list(set(familiar_words)-set(unfamiliar_words))
    new_words=list(set(self.new_words)-set(familiar_words))
    unfamiliar_words+=new_words
    for word in unfamiliar_words:
      if word in word_dict_score:
        new_score=max(word_dict_score[word]-1,0)
        word_dict_score[word]=new_score
        word_dict_timestamp[word]=(int(time.time())+5*(int(new_score))**2*60)
      else:
        word_dict_score[word]=0
        word_dict_timestamp[word]=int(time.time())
    for word in familiar_words:
      if word in word_dict_score:
        new_score=min(word_dict_score[word]+1,self.max_score)
        word_dict_score[word]=new_score
        word_dict_timestamp[word]=(int(time.time())+10*(int(new_score)+1)**3*60)

    self.words=np.array(list(word_dict_score.keys()))
    self.scores=np.array(list(word_dict_score.values()))
    self.timestamps=np.array(list(word_dict_timestamp.values()))
    self.save_score()
    current_time=int(time.time())
    #Select words with proficiency score less than self.max_score
    idx_learning=np.where((self.scores<self.max_score)*((self.timestamps<current_time)))[0]
    print(idx_learning.shape[0],self.scores.sum())
    np.random.shuffle(idx_learning)
    idx_learning=idx_learning[:1000]
    self.word_learning=self.words[idx_learning]
    self.score_leaning=self.scores[idx_learning]
    msg=[f"{self.word_learning[i]}: {self.max_score-self.score_leaning[i]}, " for i in range(len(idx_learning))]
    self.msg_user=self.msg_user_format.format("".join(msg))
