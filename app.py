from gogaku.streamlit.main_page_gemini import main_page
from gogaku.streamlit.language_setting_gemini import language_setting
from gogaku.streamlit.system_setting_gemini import system_setting_gemini,load_settings,update_vm_setting
import streamlit as st
from gogaku.vocab_manager.vocab_manager_gemini import Vocab_Manager_Gemini
from google import genai
from google.cloud import texttospeech
import json
import time
from sudachipy import tokenizer
from sudachipy import dictionary
from chinese import ChineseAnalyzer

def init_page():
  with open('language_codes.json') as f:
    #st.session_state['lang_code_list']=json.load(f)
    st.session_state['lang_dict_list']=json.load(f)
    st.session_state['langs_list']=list(st.session_state['lang_dict_list'].keys())
    #st.session_state['lang_code_list']=[l.split('_')[0] for l in st.session_state['lang_dict_list'].values()]
  st.session_state['tts_client']=texttospeech.TextToSpeechClient()
  st.session_state['time']=time.time() # current time in seconds

  st.session_state['practice']=False
  st.session_state['language_setting']=False
  st.session_state['system_setting']=False
  st.session_state['vm']=Vocab_Manager_Gemini()
  st.session_state['additional_words']=[]
  load_settings()
  if st.session_state['param']['current_language']!=None:
    if 'Japanese' in st.session_state['param']['current_language']:
      mode = tokenizer.Tokenizer.SplitMode.C
      st.session_state['japanese_tokenizer']=dictionary.Dictionary().create(mode=mode)
    elif 'Chinese' in st.session_state['param']['current_language']:
      st.session_state['chinese_analyzer']=ChineseAnalyzer()
    elif st.session_state['param']['current_language'] not in ['Japanese','Chinese','Korean']:
      import spacy
      st.session_state['nlp']=spacy.load(st.session_state['lang_dict_list'][st.session_state['param']['current_language']])
  if st.session_state['param']['gemini_api_key']=='':
    st.session_state['system_setting']=True
  elif st.session_state['param']['current_language'] is None:
    st.session_state['language_setting']=True
    st.session_state['gemini_client']=genai.Client(api_key=st.session_state['param']['gemini_api_key'])
  else:
    st.session_state['practice']=True
    st.session_state['gemini_client']=genai.Client(api_key=st.session_state['param']['gemini_api_key'])
    update_vm_setting()

def main():
  if 'init' not in st.session_state:
    init_page()
    st.session_state['init']='done'
  if st.session_state['practice']:
    main_page()
  elif st.session_state['language_setting']:
    language_setting()
  elif st.session_state['system_setting']:
    system_setting_gemini()
  
if __name__ == "__main__":
    main()
