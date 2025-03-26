from gogaku.streamlit.setup import load_settings,update_vm_setting
from gogaku.streamlit.main_page import main_page
from gogaku.streamlit.language_setting import language_setting
import streamlit as st
from gogaku.vocab_manager import Vocab_Manager
import asyncio

def main():
  if 'init' not in st.session_state:
    st.set_page_config(initial_sidebar_state="collapsed")
    st.session_state['practice']=False
    st.session_state['language_setting']=True
    load_settings()
    st.session_state['vm']=Vocab_Manager()
    st.session_state['init']='done'
    if st.session_state['current_language'] is not None:
      update_vm_setting()
  if st.session_state['practice']:
    asyncio.run(main_page())
  elif st.session_state['language_setting']:
    language_setting()
  
if __name__ == "__main__":
    main()
