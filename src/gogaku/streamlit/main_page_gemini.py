import streamlit as st
from gogaku.tts import synthesize_text
from gogaku.streamlit.system_setting_gemini import save_settings
import re
import base64
import time
from chinese.tokenizer import Tokenizer

def update_and_generate(vm,unfamiliar_words=None,familiar_words=None):
  if (unfamiliar_words is not None) or (familiar_words is not None):
    vm.update_score(unfamiliar_words,familiar_words)
  vm.generate_sentence()

def main_page():
  current_language=st.session_state['param']['current_language']
  param_language=st.session_state['param']['languages'][current_language]
  st.header(f"{param_language['proficiency']} {current_language}!")
  
  if "unfamiliar_word" not in st.session_state:
    st.session_state["unfamiliar_word"]=None
    st.session_state["familiar_word"]=None
  if "sentence" not in st.session_state:
    update_and_generate(st.session_state["vm"],st.session_state["unfamiliar_word"],st.session_state["familiar_word"])
    st.session_state["sentence"]=st.session_state["vm"].sentence
    st.session_state["translation"]=st.session_state["vm"].translation
    st.session_state["explanation"]=st.session_state["vm"].explanation
    audio_bytes=synthesize_text(st.session_state['tts_client'],
                    st.session_state["sentence"],
                    param_language['speaker_code'],
                    param_language['speaker_name'])
    audio_base64=base64.b64encode(audio_bytes).decode()
    st.session_state['audio_tag'] = f'<audio controls autoplay="true" src="data:audio/wav;base64,{audio_base64}">'
    if 'Japanese' in st.session_state['param']['current_language']:
      words=[token.surface() for token in st.session_state['japanese_tokenizer'].tokenize(re.sub(r'[^\w\s\']', '', st.session_state["sentence"]))]
    elif 'Chinese' in st.session_state['param']['current_language']:
      words=st.session_state['chinese_analyzer'].parse(re.sub(r'[^\w\s\']', '', st.session_state["sentence"]),using=Tokenizer.pynlpir).tokens()
    else:
      words=re.sub(r'[^\w\s\']', ' ', st.session_state["sentence"]).split(' ')
    st.session_state['words']=[word for word in words if len(word.replace(' ','')) > 0]
    st.session_state['time']=time.time()
    
  st.markdown(st.session_state['audio_tag'],unsafe_allow_html=True)
  st.audio_input("Check your pronunciation")
  with st.expander('Show text',expanded=False):
    st.write(st.session_state["sentence"])
    choose_unfamiliar_word()
  with st.expander("Details",expanded=False):
    st.markdown(st.session_state["translation"])
    st.markdown(st.session_state["explanation"])
      
  col1,col2,col3=st.columns(3)
  with col1:
    if st.button("Next"):
      del st.session_state["sentence"]
      study_time=time.time()-st.session_state['time']
      st.session_state['param']['languages'][current_language]['study_time']+=study_time
      save_settings()
      st.session_state['time']=time.time()
      st.rerun()
  with col2:
    if st.button('Change Language Settings'):
      st.session_state['practice']=False
      st.session_state['language_setting']=True
      study_time=time.time()-st.session_state['time']
      st.session_state['param']['languages'][current_language]['study_time']+=study_time
      st.session_state["vm"].update_score(st.session_state["unfamiliar_word"],st.session_state["familiar_word"])
      save_settings()
      st.rerun()
  with col3:
    if st.button('System Settings'):
      st.session_state['practice']=False
      st.session_state['system_setting']=True
      study_time=time.time()-st.session_state['time']
      st.session_state['param']['languages'][current_language]['study_time']+=study_time
      st.session_state["vm"].update_score(st.session_state["unfamiliar_word"],st.session_state["familiar_word"])
      save_settings()
      st.rerun()
  if st.button('Reset timer'):
    st.session_state['time']=time.time()
  
  total_study_time=st.session_state['param']['languages'][current_language]['study_time']
  # Convert to hours, minutes, seconds
  hours = int(total_study_time // 3600)
  minutes = int((total_study_time % 3600) // 60)
  seconds = int(total_study_time % 60)
  # Format the time string
  time_string = f"{hours:02}:{minutes:02}:{seconds:02}"
  st.write('Total study time: ',time_string)

def choose_unfamiliar_word():
  #if 'Japanese' in st.session_state['param']['current_language']:
  #  words=[token.surface() for token in st.session_state['japanese_tokenizer'].tokenize(re.sub(r'[^\w\s\']', '', st.session_state["sentence"]))]
  #elif 'Chinese' in st.session_state['param']['current_language']:
  #  words=st.session_state['chinese_analyzer'].parse(re.sub(r'[^\w\s\']', '', st.session_state["sentence"]),using=Tokenizer.pynlpir).tokens()
  #else:
  #  words=re.sub(r'[^\w\s\']', ' ', st.session_state["sentence"]).split(' ')
  #words=[word for word in words if len(word) > 0]
  clicked_words=st.pills("Click the words you don't understand.", st.session_state['words'],selection_mode="multi")
  st.session_state["unfamiliar_word"]=list(set(clicked_words))
  st.session_state["familiar_word"]=list(set(st.session_state['words'])-set(clicked_words))
