import streamlit as st
import json,os
from gogaku.vocab_manager import Vocab_Manager

def setup_page():
  st.title("Settings")
  
  # User selects the language to learn
  if 'current_language' not in st.session_state:
    idx=0
  else:
    idx=st.session_state['language'].index(st.session_state['current_language'])
  language=st.selectbox("Select language",st.session_state['language'],index=idx)
  
  # User selects their proficiency level
  if 'proficiency' not in st.session_state:
    idx=0
  else:
    idx=st.session_state['levels'].index(st.session_state['proficiency'][st.session_state['current_language']])
  proficiency=st.selectbox("Select level",st.session_state['levels'],index=idx)
  
  st.session_state['language']=language
  st.session_state['proficiency']=proficiency
  if 'vm' in st.session_state:
    del st.session_state['vm']

def system_setting():
  st.title("System Settings")

  if 'LLM_URL' not in st.session_state:
    st.session_state['LLM_URL']=''
  default_url = 'http://127.0.0.1:1234'
  msg=f'Leave blank for default: {default_url}'
  url=st.text_input("Type the URL to your LLM server",st.session_state['LLM_URL'],placeholder=msg)
  if len(url)==0:
    url=default_url
  st.session_state['LLM_URL']=url.replace(' ','')

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
  st.session_state['LLM_URL']=settings['LLM_URL']
  st.session_state['dir_vocab']=settings['dir_vocab']
  os.makedirs(st.session_state['dir_vocab'],exist_ok=True)
  save_settings()

def initial_settings():
  settings={'proficiency':{},
            'current_language':None,
            'levels':['A1','A2','B1','B2','C1','C2'],
            'MAX_SCORE':5,
            'LLM_URL':'http://127.0.0.1:1234',
            'dir_vocab':'./vocab_data/'}
  return settings

def save_settings():
  settings={'proficiency':st.session_state['proficiency'],
            'current_language':st.session_state['current_language'],
            'levels':st.session_state['levels'],
            'MAX_SCORE':st.session_state['MAX_SCORE'],
            'LLM_URL':st.session_state['LLM_URL'],
            'dir_vocab':st.session_state['dir_vocab']}
  with open('./settings.json','w') as f:
    json.dump(settings,f,indent=2)


def update_vm_setting():
  """
  Update the language model settings.
  """
  st.session_state["vm"].update_setting(st.session_state['current_language'],st.session_state['proficiency'][st.session_state['current_language']])
  save_settings()