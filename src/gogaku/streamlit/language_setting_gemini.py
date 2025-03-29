import streamlit as st
import numpy as np
import os,re
from gogaku.streamlit.system_setting_gemini import update_vm_setting
from google.genai import types

def get_first_words(language:str,level:str,num_words=50):
  """
  Generate the first 10 words for the new language at the specified level.
  """
  msg_system="You are a language learning assistant. Follow the user's instructions to generate words according to the specified language and level."
  msg=f"""Generate {num_words} {language.title()} words at the {level} level in the following format:
  <word 1>,<word 2>,...,<word {num_words}>
  Do not add any spaces after the comma.
  Do not say anything else."""
  response=st.session_state['gemini_client'].models.generate_content(
    model=st.session_state['current_model'],
    config=types.GenerateContentConfig(
      temperature=st.session_state['gemini_temperature'],
      system_instruction=msg_system),
    contents=msg)
  
  raw_text=response.text
  text=raw_text.replace('<','').replace('>','').replace('\n','').split(',')
  num_words_generated=len(text)
  if not os.path.exists(st.session_state['dir_vocab']+f'{language.lower().replace(' ','_')}.csv'):
    np.savetxt(st.session_state['dir_vocab']+f'{language.lower().replace(' ','_')}.csv',np.column_stack([text,np.zeros(num_words_generated,int)]),fmt='%s',delimiter=',',encoding='utf-8')
  
def language_setting():
  """
  Set the language and proficiency level for the user.
  """
  st.title("Language Settings")
  idx=list(st.session_state['proficiency'].keys()).index(st.session_state['current_language']) if st.session_state['current_language'] is not None else None
  language=st.selectbox("Select the language you want to learn.",list(st.session_state['proficiency'].keys()),index=idx)
  language_new=st.text_input("Or type the name of the language you want to learn in English.",placeholder='English').strip().title()
  idx=st.session_state['levels'].index(st.session_state['proficiency'][st.session_state['current_language']]) if st.session_state['current_language'] is not None else 0
  proficiency=st.selectbox("Select your level.",st.session_state['levels'],index=idx,)
  vm_request=st.text_area("Any specific requests for the language model?",st.session_state['vm_request'],placeholder='Generated sentence should have more than 10 words.')
  additional_words=st.text_area("Type words you want to learn",placeholder='word1 word2 ...',label_visibility='collapsed')
  st.session_state['additional_words']=re.sub(r'[^\w\s\']','',additional_words).split(' ')

  if st.button("Confirm",disabled=((language==language_new) and (len(language_new)==0))):
    if language==language_new:
      st.session_state['current_language']=language
      st.session_state['practice']=True
      st.session_state['language_setting']=False
      if vm_request!=st.session_state['vm_request']:
        st.session_state['vm_request']=vm_request
        update_vm_setting(vm_request)
      st.rerun()
    elif len(language_new)!=0 and language_new not in st.session_state['proficiency']:
      st.session_state['proficiency'][language_new]=proficiency
      st.session_state['current_language']=language_new
      if not os.path.exists(st.session_state['dir_vocab']+f'{language_new.lower()}.csv'):
        get_first_words(language_new,proficiency)
      st.session_state['vm_request']=vm_request
      update_vm_setting(vm_request)
      st.session_state['practice']=True
      st.session_state['language_setting']=False
      if 'vm_task' in st.session_state: del st.session_state['vm_task']
      st.rerun()
    elif len(language_new)!=0 and language_new in st.session_state['proficiency']:
      st.session_state['current_language']=language_new
      st.session_state['vm_request']=vm_request
      update_vm_setting(vm_request)
      st.session_state['practice']=True
      st.session_state['language_setting']=False
      if 'vm_task' in st.session_state: del st.session_state['vm_task']
      st.rerun()
    else:
      st.session_state['current_language']=language 
      st.session_state['vm_request']=vm_request
      st.session_state['proficiency'][st.session_state['current_language']]=proficiency
      update_vm_setting(vm_request)
      st.session_state['practice']=True
      st.session_state['language_setting']=False
      if 'vm_task' in st.session_state: del st.session_state['vm_task']
      st.rerun()