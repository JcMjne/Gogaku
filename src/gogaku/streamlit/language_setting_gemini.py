import streamlit as st
import numpy as np
import os,re
from gogaku.streamlit.system_setting_gemini import update_vm_setting,save_settings
from google.genai import types

_init_dict_lang={
  'proficiency':{},
  'speaker_language':''
}

def get_first_words(language:str,level:str,num_words=50):
  """
  Generate the first 10 words for the new language at the specified level.
  """
  msg_system="You are a language learning assistant. Follow the user's instructions to generate words according to the specified language and level."
  msg=f"""Generate {num_words} {language.title()} words at the {level} level in the following format:
  <word 1>,<word 2>,...,<word {num_words}>
  Do not add any spaces after the comma. \
    Do not say anything else."""
  response=st.session_state['gemini_client'].models.generate_content(
    model=st.session_state['param']['current_model'],
    config=types.GenerateContentConfig(
      temperature=st.session_state['param']['gemini_temperature'],
      system_instruction=msg_system),
    contents=msg)
  
  raw_text=response.text
  text=raw_text.replace('<','').replace('>','').replace('\n','').split(',')
  num_words_generated=len(text)
  if not os.path.exists(st.session_state['param']['dir_vocab']+f'{language.lower().replace(' ','_')}.csv'):
    np.savetxt(st.session_state['param']['dir_vocab']+f'{language.lower().replace(' ','_')}.csv',
               np.column_stack([text,np.zeros(num_words_generated,int)]),fmt='%s',delimiter=',',encoding='utf-8')
  
def language_setting():
  """
  Set the language and proficiency level for the user.
  """
  st.title("Language Settings")
  idx=list(st.session_state['param']['languages'].keys()).index(st.session_state['param']['current_language']) if st.session_state['param']['current_language'] is not None else None
  language=st.selectbox("Select the language you want to learn.",list(st.session_state['param']['languages'].keys()),index=idx)
  language_new=st.text_input("Or type the name of the language you want to learn in English.",placeholder='English').strip().title()
  current_language=language_new if len(language_new)!=0 else language
  idx=st.session_state['param']['levels'].index(st.session_state['param']['languages'][current_language]['proficiency']) if current_language in st.session_state['param']['languages'] else 0
  proficiency=st.selectbox("Select your level.",st.session_state['param']['levels'],index=idx)
  with st.expander("Additional Settings",expanded=False):
    val=st.session_state['param']['languages']['vm_request'] if ('current_language' in st.session_state['param']['languages']) else ''
    vm_request=st.text_area("Any specific requests for the language model?",val,placeholder='Generated sentence should have more than 10 words.')
    additional_words=st.text_area("Type words you want to learn",placeholder='word1 word2 ...')
  st.session_state['additional_words']=re.sub(r'[^\w\s\']','',additional_words).split(' ')
  
  #Set language code for audio
  if st.button('Enable Audio' if not st.session_state['audio_enabled'] else 'Disable Audio',disabled=(current_language is None)):
    
    update_language_settings(language,language_new,proficiency,vm_request)
    st.session_state['audio_enabled']=not st.session_state['audio_enabled']
    st.rerun()
  if st.session_state['audio_enabled']:
    update_language_settings(language,language_new,proficiency,vm_request)
    speaker_language_settings()
  
  if st.button("Confirm",disabled=((language==language_new) and (len(language_new)==0))):
    update_language_settings(language,language_new,proficiency,vm_request)
    st.session_state['practice']=True
    st.session_state['language_setting']=False
    st.rerun()

def update_language_settings(language,language_new,proficiency,vm_request):
  if language==language_new:
    st.session_state['param']['current_language']=language
    if vm_request!=st.session_state['param']['languages'][language]['vm_request']:
      st.session_state['param']['languages'][language]['vm_request']=vm_request
      update_vm_setting(vm_request)
    
  elif len(language_new)!=0 and language_new not in st.session_state['param']['languages']:
    st.session_state['param']['current_language']=language_new
    st.session_state['param']['languages'][language_new]={'proficiency':proficiency,}
    if not os.path.exists(st.session_state['param']['dir_vocab']+f'{language_new.lower()}.csv'):
      get_first_words(language_new,proficiency)
    st.session_state['param']['languages'][language_new]['vm_request']=vm_request
    update_vm_setting(vm_request)
    if 'vm_task' in st.session_state: del st.session_state['vm_task']
    
  elif len(language_new)!=0 and language_new in st.session_state['param']['languages']:
    st.session_state['param']['current_language']=language_new
    st.session_state['param']['languages'][language_new]['vm_request']=vm_request
    st.session_state['param']['languages'][language_new]['proficiency']=proficiency
    update_vm_setting(vm_request)
    if 'vm_task' in st.session_state: del st.session_state['vm_task']
    
  else: # if language_new is blank
    st.session_state['param']['current_language']=language 
    st.session_state['param']['languages'][language]['vm_request']=vm_request
    st.session_state['param']['languages'][language]['proficiency']=proficiency
    update_vm_setting(vm_request)
    if 'vm_task' in st.session_state: del st.session_state['vm_task']
  save_settings()

def speaker_language_settings():
  current_language=st.session_state['param']['current_language']
  param_language=st.session_state['param']['languages'][current_language]
  if 'speaker_language' in param_language:
    idx=list(list(st.session_state['lang_code_list'].keys())).index(param_language['speaker_language'])
  else:
    idx=0
  param_language['speaker_language']=st.selectbox("Select speaker's language",list(st.session_state['lang_code_list'].keys()),index=idx)
  speaker_code_short=st.session_state['lang_code_list'][param_language['speaker_language']]
  voices=st.session_state['tts_client'].list_voices(language_code=speaker_code_short)
  speaker_names=[f'{i}: '+' '.join(v.name.split('-')[1:])+f' ({v.ssml_gender.name})' for i,v in enumerate(voices.voices)]
  voice_names=[v.name for v in voices.voices]
  idx=voice_names.index(param_language['speaker_name']) if 'speaker_name' in param_language and param_language['speaker_name'] in voice_names else 0
  speaker_name=st.selectbox("Select speaker's name",speaker_names,index=idx)
  speaker_name_idx=int(speaker_name.split(':')[0])
  param_language['speaker_code']=voices.voices[speaker_name_idx].language_codes[0]
  param_language['speaker_name']=voices.voices[speaker_name_idx].name
  param_language['speaking_rate']=st.slider("Speaking speed. 1.0 is the normal native speed",
                                            min_value=0.25,max_value=4.0,step=0.05,
                                            value=param_language['speaking_rate'] if 'speaking_rate' in param_language else 1.0)
  
  