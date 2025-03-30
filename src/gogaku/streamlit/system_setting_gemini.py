import streamlit as st
import json,os
from google import genai

def system_setting_gemini():
  st.title("System Settings")
  st.session_state['param']['user_language']=st.text_input("Type your native language",st.session_state['param']['user_language'])
  gemini_api_key=st.text_input("Type Gemini API Key",st.session_state['param']['gemini_api_key'],type="password")

  if len(gemini_api_key)!=0:
    st.session_state['param']['gemini_api_key']=gemini_api_key
    
  txt_temp="Use higher values for more creative responses, and lower values for more deterministic responses."
  st.session_state['param']['gemini_temperature']=st.slider(
    txt_temp,min_value=0.0,max_value=2.0,value=st.session_state['param']['gemini_temperature'],step=0.1)
  idx=st.session_state['param']['LLM_models'].index(st.session_state['param']['current_model'])
  st.session_state['param']['current_model']=st.selectbox("Select the model",st.session_state['param']['LLM_models'],index=idx)
  
  if st.button("Confirm",disabled=(st.session_state['param']['gemini_api_key']=='')):
    save_settings()
    st.session_state['gemini_client']=genai.Client(api_key=st.session_state['param']['gemini_api_key'])
    if st.session_state['param']['current_language'] is None:
      st.session_state['language_setting']=True
      st.session_state['system_setting']=False
    else:
      st.session_state['practice']=True
      st.session_state['system_setting']=False
    update_vm_setting()
    st.rerun()

def load_settings():
  if not os.path.exists('./settings.json'):
    settings=initial_settings()
  else:
    with open('./settings.json') as f:
      settings=json.load(f)
  st.session_state['param']=settings
  os.makedirs(st.session_state['param']['dir_vocab'],exist_ok=True)
  save_settings()

def initial_settings():
  settings={'current_language':None,
            'levels':['Beginner','High-Beginner','Intermediate','High Intermediate','Advanced'],
            'MAX_SCORE':5,
            'LLM_models':['gemini-2.0-flash','gemini-2.0-flash-lite'],
            'current_model':'gemini-2.0-flash',
            'dir_vocab':'./vocab_data/',
            'gemini_api_key':'',
            'gemini_temperature':0.5,
            'user_language':'English',
            'speaking_rate':1.0,
            'speaking_pitch':0.0,
            'languages':{}}
  return settings

def save_settings():
  with open('./settings.json','w') as f:
    #json.dump(settings,f,indent=2)
    json.dump(st.session_state['param'],f,indent=2)

def update_vm_setting(request=''):
  """
  Update the language model settings.
  """
  current_language=st.session_state['param']['current_language']
  proficiency=st.session_state['param']['languages'][current_language]['proficiency']
  st.session_state["vm"].update_setting(current_language,proficiency,request=request)
  if 'sentence' in st.session_state:
    del st.session_state['sentence']
  save_settings()