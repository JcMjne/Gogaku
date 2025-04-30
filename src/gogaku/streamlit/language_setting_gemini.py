import streamlit as st
import numpy as np
import os,time,re
from gogaku.streamlit.system_setting_gemini import update_vm_setting,save_settings
from sudachipy import tokenizer
from sudachipy import dictionary
from chinese import ChineseAnalyzer
from wordfreq import top_n_list
from chinese.tokenizer import Tokenizer

def get_first_words(language:str,num_words=5000):
  """
  Generate the first num_words words for the new language at the specified level.
  """
  lang_code=st.session_state['lang_dict_list'][st.session_state['param']['current_language']].split('_')[0]
  words=top_n_list(lang_code,num_words)
  #extract only words
  words=[words[i] for i in range(len(words)) if (words[i].isalpha() and len(words[i])>1)]
  if st.session_state['param']['current_language']=='Chinese':
    word_processed=st.session_state['chinese_analyzer'].parse(re.sub(r'[^\w\s\']', '',' '.join(words)),using=Tokenizer.pynlpir).tokens()
    word_processed=[word.replace(' ','') for word in word_processed if len(word.replace(' ','')) > 0]
  elif st.session_state['param']['current_language']=='Japanese':
    word_processed=[token.surface() for token in st.session_state['japanese_tokenizer'].tokenize(re.sub(r'[^\w\s\']', '',' '.join(words)))]
    word_processed=[word.replace(' ','') for word in word_processed if len(word.replace(' ','')) > 0]
  else:
    docs=list(st.session_state['nlp'].pipe(words))
    words_lemma=[[token.lemma_ for token in doc] for doc in docs]
    word_processed=list(set(' '.join([word.lower() for sublist in words_lemma for word in sublist]).split(' ')))

  num_words_generated=len(word_processed)
  current_time=int(time.time())
  time_column = [current_time] * num_words_generated
  np.savetxt(st.session_state['param']['dir_vocab']+f"{language.lower().replace(' ','_')}.csv",
              np.column_stack([word_processed,np.zeros(num_words_generated,int),time_column]),fmt='%s',delimiter=',',encoding='utf-16')
  
def language_setting():
  """
  Set the language and proficiency level for the user.
  """
  st.header("Language Settings")
  idx=st.session_state['langs_list'].index(st.session_state['param']['current_language']) if st.session_state['param']['current_language'] is not None else None
  current_language=st.selectbox("Select the language you want to learn.",st.session_state['langs_list'],index=idx)
  default_proficiency=st.session_state['param']['languages'][current_language]['proficiency'] if current_language in st.session_state['param']['languages'] else 'Beginner'
  proficiency=st.text_input("Describe your level.",value=default_proficiency)
  with st.expander("Additional Settings",expanded=False):
    val=st.session_state['param']['languages'][current_language]['vm_request'] if (current_language in st.session_state['param']['languages']) else ''
    vm_request=st.text_area("Any specific requests for the language model?",val)
    st.session_state['additional_words']=st.text_area("Type words you want to learn")
  
  st.session_state['param']['current_language']=current_language
  if st.session_state['param']['current_language'] is not None:
    speaker_language_settings(current_language)
  if current_language not in st.session_state['param']['languages']:
    st.session_state['auto_vocab']=st.checkbox('Automatically add most frequency words to vocabulary list',value=True)
    if st.session_state['auto_vocab']:
      st.session_state['num_words']=int(st.number_input('Number of words to add',min_value=0,step=1,value=3000))

  if st.button("Confirm",disabled=(current_language==None)):
    if 'Japanese' in st.session_state['param']['current_language']:
      if 'japanese_tokenizer' not in st.session_state:
        mode=tokenizer.Tokenizer.SplitMode.C
        st.session_state['japanese_tokenizer']=dictionary.Dictionary().create(mode=mode)
    elif 'Chinese' in st.session_state['param']['current_language']:
      if 'chinese_analyzer' not in st.session_state:
        st.session_state['chinese_analyzer']=ChineseAnalyzer()
    update_language_settings(current_language,proficiency,vm_request)
    st.session_state['practice']=True
    st.session_state['language_setting']=False
    st.rerun()

def update_language_settings(current_language,proficiency,vm_request):
  st.session_state['param']['current_language']=current_language
  if 'vm_task' in st.session_state: del st.session_state['vm_task']
  if current_language not in st.session_state['param']['languages']: #new language
    if current_language not in ['Japanese','Chinese']:
      os.system(f"python -m spacy download {st.session_state['lang_dict_list'][current_language]}")
      import spacy
      st.session_state['nlp']=spacy.load(st.session_state['lang_dict_list'][current_language])
    st.session_state['param']['languages'][current_language]={}
    if not os.path.exists(st.session_state['param']['dir_vocab']+f'{current_language.lower()}.csv'):
      if st.session_state['auto_vocab']:
        get_first_words(current_language,st.session_state['num_words'])
      else:
        get_first_words(current_language,0)

    st.session_state['param']['languages'][current_language]['study_time']=0.0
    
  st.session_state['param']['languages'][current_language]['vm_request']=vm_request
  st.session_state['param']['languages'][current_language]['proficiency']=proficiency
  st.session_state['param']['languages'][current_language]['speaker_name']=st.session_state['speaker_name']
  st.session_state['param']['languages'][current_language]['speaker_code']='-'.join(st.session_state['speaker_name'].split('-')[:2])
  update_vm_setting(vm_request)
  st.session_state["unfamiliar_word"]=None
  st.session_state["familiar_word"]=None
  st.session_state['time']=time.time()
  save_settings()

def speaker_language_settings(current_language):
  param_language=st.session_state['param']['languages'][current_language] if current_language in st.session_state['param']['languages'] else {}
  speaker_code_short=st.session_state['lang_dict_list'][current_language].split('_')[0]
  voices=st.session_state['tts_client'].list_voices(language_code=speaker_code_short)
  speaker_names=[f'{i}: '+' '.join(v.name.split('-')[1:])+f' ({v.ssml_gender.name})' for i,v in enumerate(voices.voices)]
  voice_names=[v.name for v in voices.voices]
  idx=voice_names.index(param_language['speaker_name']) if 'speaker_name' in param_language and param_language['speaker_name'] in voice_names else 0
  speaker_name=st.selectbox("Select speaker's name",speaker_names,index=idx)
  speaker_name_idx=int(speaker_name.split(':')[0])
  st.session_state['speaker_name']=voices.voices[speaker_name_idx].name
  
  