import streamlit as st
from gogaku.tts import synthesize_text
import re
import base64

def update_and_generate(vm,unfamiliar_words=None,familiar_words=None):
  if (unfamiliar_words is not None) or (familiar_words is not None):
    vm.update_score(unfamiliar_words,familiar_words)
  vm.generate_sentence()

def main_page():
  current_language=st.session_state['param']['current_language']
  param_language=st.session_state['param']['languages'][current_language]
  st.title(f"Practice {param_language['proficiency']} level {current_language}!")
  
  if "unfamiliar_word" not in st.session_state:
    st.session_state["unfamiliar_word"]=None
    st.session_state["familiar_word"]=None
  if "sentence" not in st.session_state:
    update_and_generate(st.session_state["vm"],st.session_state["unfamiliar_word"],st.session_state["familiar_word"])
    st.session_state["sentence"]=st.session_state["vm"].sentence
    st.session_state["translation"]=st.session_state["vm"].translation
    st.session_state["explanation"]=st.session_state["vm"].explanation
    if st.session_state['audio_enabled']:
      synthesize_text(st.session_state['tts_client'],
                      st.session_state["sentence"],
                      param_language['speaker_code'],
                      param_language['speaker_name'],
                      param_language['speaking_rate'],
                      st.session_state['param']['speaking_pitch'])
    
  if "sentence" in st.session_state:
    if st.session_state['audio_enabled']:
      st.audio('text_audio.mp3', format='audio/mp3',autoplay=True)
      with st.expander('Show text',expanded=False):
        st.write(st.session_state["sentence"])
        choose_unfamiliar_word()
    else:
      st.subheader(st.session_state["sentence"])
      choose_unfamiliar_word()
    with st.expander("Details",expanded=False):
      st.write(st.session_state["translation"])
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
  words=re.sub(r'[^\w\s\']', '', st.session_state["sentence"]).split(' ')
  words= [word for word in words if len(word) > 0]
  clicked_words=st.pills("Click the words you don't understand.", words,selection_mode="multi")
  st.session_state["unfamiliar_word"]=list(set(clicked_words))
  st.session_state["familiar_word"]=list(set(words)-set(clicked_words))

def play_audio(audio_path='text_audio.mp3'):
  audio_placeholder=st.empty()
  file_=open(audio_path, "rb")
  contents = file_.read()
  file_.close()
  audio_str = "data:audio/ogg;base64,%s"%(base64.b64encode(contents).decode())
  audio_html = """
                  <audio autoplay=True>
                  <source src="%s" type="audio/ogg" autoplay=True>
                  Your browser does not support the audio element.
                  </audio>
              """ %audio_str
  #audio_placeholder.empty()
  audio_placeholder.markdown(audio_html, unsafe_allow_html=True)