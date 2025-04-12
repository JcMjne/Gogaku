import streamlit as st
from gogaku.tts import synthesize_text
import re
import base64
import uuid

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
    sentence=st.session_state["sentence"]=st.session_state["vm"].sentence
    if ('Japanese' in st.session_state['param']['current_language']) or ('Chinese' in st.session_state['param']['current_language']):
      sentence=sentence.replace(' ','')
    st.session_state["sentence"]=st.session_state["vm"].sentence
    st.session_state["translation"]=st.session_state["vm"].translation
    st.session_state["explanation"]=st.session_state["vm"].explanation
    if st.session_state['param']['audio_enabled']:
      audio_bytes=synthesize_text(st.session_state['tts_client'],
                      sentence,
                      param_language['speaker_code'],
                      param_language['speaker_name'],
                      param_language['speaking_rate'],
                      st.session_state['param']['speaking_pitch'])
      audio_base64=base64.b64encode(audio_bytes).decode()
      st.session_state['audio_tag'] = f'<audio controls autoplay="true" src="data:audio/wav;base64,{audio_base64}">'
    
  if "sentence" in st.session_state:
    sentence=st.session_state["vm"].sentence
    if ('Japanese' in st.session_state['param']['current_language']) or ('Chinese' in st.session_state['param']['current_language']):
      sentence=sentence.replace(' ','')
    if st.session_state['param']['audio_enabled']:
      st.markdown(st.session_state['audio_tag'],unsafe_allow_html=True)
      with st.expander('Show text',expanded=False):
        st.write(st.session_state["sentence"])
        choose_unfamiliar_word()
    else:
      st.subheader(st.session_state["sentence"])
      choose_unfamiliar_word()
    with st.expander("Details",expanded=False):
      st.markdown(st.session_state["translation"])
      st.markdown(st.session_state["explanation"])
  
  col1,col2,col3=st.columns(3)
  with col1:
    if st.button("Next"):
      del st.session_state["sentence"]
      st.rerun()
  with col2:
    if st.button('Change Language Settings'):
      st.session_state['practice']=False
      st.session_state['language_setting']=True
      st.rerun()
  with col3:
    if st.button('System Settings'):
      st.session_state['practice']=False
      st.session_state['system_setting']=True
      st.rerun()

def choose_unfamiliar_word():
  words=re.sub(r'[^\w\s\']', ' ', st.session_state["sentence"]).split(' ')
  words= [word for word in words if len(word) > 0]
  clicked_words=st.pills("Click the words you don't understand.", words,selection_mode="multi")
  st.session_state["unfamiliar_word"]=list(set(clicked_words))
  st.session_state["familiar_word"]=list(set(words)-set(clicked_words))
