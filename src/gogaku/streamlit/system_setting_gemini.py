import streamlit as st
import json,os
from google import genai

def system_setting_gemini():
  st.title("System Settings")
  st.session_state['user_language']=st.text_input("Type your native language",st.session_state['user_language'])
  gemini_api_key=st.text_input("Type Gemini API Key",st.session_state['gemini_api_key'],type="password")

  if len(gemini_api_key)!=0:
    st.session_state['gemini_api_key']=gemini_api_key

  txt_temp="Use higher values for more creative responses, and lower values for more deterministic responses."
  st.session_state['gemini_temperature']=st.slider(txt_temp,min_value=0.0,max_value=2.0,value=st.session_state['gemini_temperature'],step=0.1)
  idx=st.session_state['LLM_models'].index(st.session_state['current_model'])
  st.session_state['current_model']=st.selectbox("Select the model",st.session_state['LLM_models'],index=idx)
  if st.button("Confirm",disabled=(st.session_state['gemini_api_key']=='')):
    save_settings()
    st.session_state['gemini_client']=genai.Client(api_key=st.session_state['gemini_api_key'])
    if st.session_state['current_language'] is None:
      st.session_state['language_setting']=True
      st.session_state['system_setting']=False
    else:
      st.session_state['practice']=True
      st.session_state['system_setting']=False
    st.rerun()

def load_settings():
  if not os.path.exists('./settings.json'):
    settings=initial_settings()
  else:
    with open('./settings.json') as f:
      settings=json.load(f)
  st.session_state['proficiency']=settings['proficiency']
  st.session_state['current_language']=settings['current_language']
  st.session_state['levels']=settings['levels']
  st.session_state['MAX_SCORE']=settings['MAX_SCORE']
  st.session_state['LLM_models']=settings['LLM_models']
  st.session_state['current_model']=settings['current_model']
  st.session_state['dir_vocab']=settings['dir_vocab']
  st.session_state['gemini_api_key']=settings['gemini_api_key']
  st.session_state['gemini_temperature']=settings['gemini_temperature']
  st.session_state['user_language']=settings['user_language']
  os.makedirs(st.session_state['dir_vocab'],exist_ok=True)
  save_settings()

def initial_settings():
  settings={'proficiency':{},
            'current_language':None,
            'levels':['Beginner','High-Beginner','Intermediate','High Intermediate','Advanced'],
            'MAX_SCORE':5,
            'LLM_models':['gemini-2.0-flash','gemini-2.0-flash-lite'],
            'current_model':'gemini-2.0-flash',
            'dir_vocab':'./vocab_data/',
            'gemini_api_key':'',
            'gemini_temperature':0.5,
            'user_language':'Japanese'}
  return settings

def save_settings():
  settings={'proficiency':st.session_state['proficiency'],
            'current_language':st.session_state['current_language'],
            'levels':st.session_state['levels'],
            'MAX_SCORE':st.session_state['MAX_SCORE'],
            'LLM_models':st.session_state['LLM_models'],
            'current_model':st.session_state['current_model'],
            'dir_vocab':st.session_state['dir_vocab'],
            'gemini_api_key':st.session_state['gemini_api_key'],
            'gemini_temperature':st.session_state['gemini_temperature'],
            'user_language':st.session_state['user_language']}
  with open('./settings.json','w') as f:
    json.dump(settings,f,indent=2)

def update_vm_setting(request=''):
  """
  Update the language model settings.
  """
  current_language=st.session_state['current_language']
  proficiency=st.session_state['proficiency'][st.session_state['current_language']]
  st.session_state["vm"].update_setting(current_language,proficiency,request=request)
  if 'sentence' in st.session_state:
    del st.session_state['sentence']
  save_settings()