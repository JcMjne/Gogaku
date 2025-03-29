from gogaku.streamlit.main_page_gemini import main_page
from gogaku.streamlit.language_setting_gemini import language_setting
from gogaku.streamlit.system_setting_gemini import system_setting_gemini,load_settings,update_vm_setting
import streamlit as st
from gogaku.vocab_manager.vocab_manager_gemini import Vocab_Manager_Gemini
from google import genai

def main():
  if 'init' not in st.session_state:
    st.session_state['practice']=False
    st.session_state['language_setting']=False
    st.session_state['system_setting']=False
    st.session_state['vm']=Vocab_Manager_Gemini()
    load_settings()
    if st.session_state['gemini_api_key']=='':
      st.session_state['system_setting']=True
    elif st.session_state['current_language'] is None:
      st.session_state['language_setting']=True
      st.session_state['gemini_client']=genai.Client(api_key=st.session_state['gemini_api_key'])
    else:
      st.session_state['practice']=True
      st.session_state['gemini_client']=genai.Client(api_key=st.session_state['gemini_api_key'])
      update_vm_setting()

    st.session_state['init']='done'
    st.session_state['vm_request']=''

  if st.session_state['practice']:
    main_page()
  elif st.session_state['language_setting']:
    language_setting()
  elif st.session_state['system_setting']:
    system_setting_gemini()
  
if __name__ == "__main__":
    main()
