from gogaku.vocab_manager.vocab_manager import Vocab_Manager
import os,datetime
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
    data=np.loadtxt(self.vocab_db_path,delimiter=",",dtype=str,encoding='utf-16')
    self.words=data[:,0]
    self.scores=data[:,1].astype(int)
    self.timestamps = data[:, 2]
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

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

  #def update_score(self,unfamiliar_words,familiar_words):
  #  """
  #  Update the proficiency scores of the words.
  #  Add words to the database if they are not already present.
  #  """
  #  word_dict_score={word:score for word,score in zip(self.words,self.scores)}
  #  word_dict_timestamp={word:timestamp for word,timestamp in zip(self.words,self.timestamps)}
  #  unfamiliar_words=[word.lower() for word in unfamiliar_words]+self.new_words
  #  unfamiliar_words=list(set(unfamiliar_words))
  #  familiar_words=[word.lower() for word in familiar_words]
  #  for word in unfamiliar_words:
  #    if word in word_dict_score:
  #      new_score=max(word_dict_score[word]-1,0)
  #      word_dict_score[word]=new_score
  #      word_dict_timestamp[word]=(datetime.datetime.now()+datetime.timedelta(minutes=5*(int(new_score)+1)**2)).strftime('%Y-%m-%d %H:%M:%S')
  #    else:
  #      word_dict_score[word]=0
  #      word_dict_timestamp[word]=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  #  for word in familiar_words:
  #    if word in word_dict_score:
  #      new_score=min(word_dict_score[word]+1,self.max_score)
  #      word_dict_score[word]=new_score
  #      word_dict_timestamp[word]=(datetime.datetime.now()+datetime.timedelta(minutes=10*(int(new_score)+1)**3)).strftime('%Y-%m-%d %H:%M:%S')
#
  #  self.words=np.array(list(word_dict_score.keys()))
  #  self.scores=np.array(list(word_dict_score.values()))
  #  self.timestamps=np.array(list(word_dict_timestamp.values()))
  #  self.save_score()
  #  current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  #  #Select words with proficiency score less than self.max_score
  #  idx_learning=np.where((self.scores<self.max_score)*((self.timestamps<current_time)))[0]
  #  self.word_learning=self.words[idx_learning]
  #  self.score_leaning=self.scores[idx_learning]
  #  idx=np.arange(len(self.word_learning))
  #  np.random.shuffle(idx)
  #  #print(idx.shape)
  #  msg=[f"{self.word_learning[idx[i]]}: {self.max_score-self.score_leaning[idx[i]]}, " for i in range(len(idx_learning))]
  #  self.msg_user=self.msg_user_format.format("".join(msg))

  def generate_sentence(self):
    """
    Generate a sentence using the language model.
    """
    response=st.session_state['gemini_client'].models.generate_content(
      model=st.session_state['param']['current_model'],
      config=types.GenerateContentConfig(
        temperature=st.session_state['param']['gemini_temperature'],
        system_instruction=self.msg_sys),
      contents=self.msg_user).text
    self.sentence=response.split('Sentence:')[1].split('Translation:')[0].strip().replace('*','')
    self.translation=response.split('Translation:')[1].split('Explanation:')[0].strip()
    self.explanation=response.split('Explanation:')[1].strip()
    self.new_words=st.session_state['additional_words']
    st.session_state['additional_words']=[]
    
  def update_setting(self,language,proficiency,request=''):
    self.new_words=[]
    self.language=language
    self.proficiency=proficiency
    self.db_dir=st.session_state['param']['dir_vocab']
    os.makedirs(self.db_dir,exist_ok=True)
    self.vocab_db_path=f'{self.db_dir}{self.language.replace(' ','_').lower()}.csv'
    self.max_score=st.session_state['param']['MAX_SCORE']
    self.msg_sys=f"""You are teaching {self.language} to {st.session_state['param']['user_language']} students at the {self.proficiency} level. \
    {"In the generated sentence, you must put space between words.\n" if ('Japanese' in self.language) or ('Chinese' in self.language) else ''} \
    Translations and explanations must be done in native level {st.session_state['param']['user_language']}. \
    The content of the explanations should also be suitable for the {self.proficiency} level students."""
              
    self.msg_user_format=f"""
    Here is a list of words followed by their priority scores; """+"""
    {}"""+f"""

    Create a natural sentence in {self.language} at the {self.proficiency} level.
    You must use more than 3 words from the list in the generated sentence.
    Prioritize higher score words in the list to create the sentence.
    The generated sentence should have more than 3 words.
    
    The output must strictly follow this format:
      Sentence:<Generated sentence >
      Translation:<Translation of generated sentence in {st.session_state['param']['user_language']}>
      Explanation:<Detailed grammatical explanation in {st.session_state['param']['user_language']}>

    In the Explanation section, describe word conjugations and meanings and so on in list format, but do not mention scores.
    At the end of Explanation, add notes about {self.proficiency} level grammatical tips used in the generated sentence.
    """+request
    self.load_score()

  def _update_setting(self,language,proficiency,request=''):
    self.new_words=[]
    self.language=language
    self.proficiency=proficiency
    self.db_dir=st.session_state['param']['dir_vocab']
    os.makedirs(self.db_dir,exist_ok=True)
    self.vocab_db_path=f'{self.db_dir}{self.language.replace(' ','_').lower()}.csv'
    self.max_score=st.session_state['param']['MAX_SCORE']
    self.msg_sys=f"""You are teaching {self.language} to {st.session_state['param']['user_language']} students at the {self.proficiency} level. \
    Follow the user's instructions carefully and generate a sentence in {self.language}. \
    In the generated sentence, if {self.language} does not use space for word segmentation, you must separate words and symbols with spaces.\n" \
    You must use {st.session_state['param']['user_language']} for all the translations and explanations. \
    The content of the explanations should also be suitable for the {self.proficiency} level students. \
    Omit the explanation of easy words for the {self.proficiency} level. \
    Do not add how to read the words in the generated sentence."""
              
    self.msg_user_format=f"""
    Here is a list of words followed by their priority scores."""+"""

    {}"""+f"""

    Please create a natural sentence in {self.language} at the {self.proficiency} level.
    Use more higher score words whenever possible.
    You do not need to use all the words.
    Also, provide 5 new {self.language} words at the {self.proficiency} level which are not in the provided list.
    
    The output must strictly follow this format:
      Sentence:<Generated sentence>
      Translation:<Translation of generated sentence in {st.session_state['param']['user_language']}>
      Explanation:<Detailed grammatical explanation in {st.session_state['param']['user_language']}>
      Words:word1,word2,word3,word4,word5

    When generating new words, you must not add space after the comma.
    In the Explanation section, describe word conjugations and meanings and so on in list format, but do not mention scores. \
    Be aware that the target students are native speakers of {st.session_state['param']['user_language']}.
    """+request
    self.load_score()

  def convert_word(self,words):
    """
    Convert verb to its base form.
    Convert noun to its singular form.

    words: list<str>
    """
    if 'Japanese' in self.language or 'Chinese' in self.language:
      return words
    msg=f"""Convert the following {self.language} words to its base form.\n
    The words are:\n
    {' '.join(words)}\n 
    The output must strictly follow this format:\n
    <word 1>,<word 2>,...,<word n>\n
    Do not include any spaces in the output. If the word is feminine adjective, make it masculine form. Do not say anything else."""
    response=st.session_state['gemini_client'].models.generate_content(
      model=st.session_state['param']['current_model'],
      config=types.GenerateContentConfig(
        temperature=0.0,
        system_instruction=self.msg_sys),
      contents=msg).text.strip().split(',')
    #print(words,response)
    return response
  
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
    unfamiliar_words=[word.lower() for word in unfamiliar_words]+self.new_words
    unfamiliar_words=list(set(unfamiliar_words))
    familiar_words=[word.lower() for word in familiar_words]
    for word in unfamiliar_words:
      if word in word_dict_score:
        new_score=max(word_dict_score[word]-1,0)
        word_dict_score[word]=new_score
        word_dict_timestamp[word]=(datetime.datetime.now()+datetime.timedelta(minutes=5*(int(new_score))**2)).strftime('%Y-%m-%d %H:%M:%S')
      else:
        word_dict_score[word]=0
        word_dict_timestamp[word]=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for word in familiar_words:
      if word in word_dict_score:
        new_score=min(word_dict_score[word]+1,self.max_score)
        word_dict_score[word]=new_score
        word_dict_timestamp[word]=(datetime.datetime.now()+datetime.timedelta(minutes=10*(int(new_score)+1)**3)).strftime('%Y-%m-%d %H:%M:%S')

    self.words=np.array(list(word_dict_score.keys()))
    self.scores=np.array(list(word_dict_score.values()))
    self.timestamps=np.array(list(word_dict_timestamp.values()))
    self.save_score()
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #Select words with proficiency score less than self.max_score
    idx_learning=np.where((self.scores<self.max_score)*((self.timestamps<current_time)))[0]
    print(idx_learning.shape[0],self.scores.sum())
    np.random.shuffle(idx_learning)
    idx_learning=idx_learning[:1000]
    self.word_learning=self.words[idx_learning]
    self.score_leaning=self.scores[idx_learning]
    #idx=np.arange(len(self.word_learning))
    #np.random.shuffle(idx)
    #msg=[f"{self.word_learning[idx[i]]}: {self.max_score-self.score_leaning[idx[i]]}, " for i in range(len(idx_learning))]
    msg=[f"{self.word_learning[i]}: {self.max_score-self.score_leaning[i]}, " for i in range(len(idx_learning))]
    self.msg_user=self.msg_user_format.format("".join(msg))
