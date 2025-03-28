import streamlit as st
import numpy as np
import requests,json,os
from gogaku.streamlit.setup import save_settings,update_vm_setting

def get_first_words(language:str,level:str,num_words=50):
  """
  Generate the first 10 words for the new language at the specified level.
  """
  url=st.session_state['LLM_URL']
  response=requests.get(f'{url}/v1/models')
  model=json.loads(response.text)['data'][0]['id']
  msg=f"""Generate {num_words} {language.title()} words at the {level} level in the following format:
  <word 1>,<word 2>,...,<word {num_words}>
  Do not add any spaces after the comma.
  Do not say anything else."""
  data={'model':model,'messages':[{'role':'user','content':msg}]}
  print(msg)
  response=requests.post(f'{url}/v1/chat/completions', json=data)
  response_content=json.loads(response.text)
  raw_text=response_content['choices'][0]['message']['content']
  text=raw_text.replace('<','').replace('>','').split(',')
  num_words_generated=len(text)
  if not os.path.exists(st.session_state['dir_vocab']+f'{language.lower().replace(' ','_')}.csv'):
    np.savetxt(st.session_state['dir_vocab']+f'{language.lower().replace(' ','_')}.csv',np.column_stack([text,np.zeros(num_words_generated,int)]),fmt='%s',delimiter=',',encoding='utf-8')
  
def language_setting():
  """
  Set the language and proficiency level for the user.
  """
  st.title("Language Settings")
  if len(st.session_state['proficiency'])>0:
    data=[f"{lang.title()} ({proficiency})," for lang,proficiency in st.session_state['proficiency'].items()]
    st.write('You are learning ',*data)

  idx=list(st.session_state['proficiency'].keys()).index(st.session_state['current_language']) if st.session_state['current_language'] is not None else None
  language=st.selectbox("Select the language you want to learn.",list(st.session_state['proficiency'].keys()),index=idx)
  language_new=st.text_input("Or type the name of the language you want to learn in English.",placeholder='English').strip().title()
  idx=st.session_state['levels'].index(st.session_state['proficiency'][st.session_state['current_language']]) if st.session_state['current_language'] is not None else 0
  proficiency=st.selectbox("Select your level.",st.session_state['levels'],index=idx,)
  vm_request=st.text_area("Any specific requests for the language model?",st.session_state['vm_request'],placeholder='Generated sentence should have more than 10 words.')
  
  if st.button("Confirm"):
    if (language is None) and (len(language_new)==0):
      st.error("Please select a language or type a new language.")
    elif language==language_new:
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

if __name__ == "__main__":
  language_setting()