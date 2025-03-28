import streamlit as st
from gogaku.vocab_manager import Vocab_Manager
import re
import asyncio

async def update_and_generate(vm,unfamiliar_words=None,familiar_words=None):
  #time.sleep(3)
  if (unfamiliar_words is not None) or (familiar_words is not None):
    vm.update_score(unfamiliar_words,familiar_words)
  vm.generate_sentence()

async def main_page():
  st.title(f"Practice {st.session_state['current_language']}!")
  if "vm_task" not in st.session_state:
    st.session_state["unfamiliar_word"]=None
    st.session_state["familiar_word"]=None
    st.session_state["vm_task"]=asyncio.create_task(update_and_generate(st.session_state["vm"]))
    
  if "sentence" in st.session_state:
    st.subheader(st.session_state["sentence"])
    words=re.sub(r'[^\w\s\']', '', st.session_state["sentence"]).split(' ')
    clicked_words=st.pills("Click the words you don't understand.", words,selection_mode="multi")
    st.session_state["unfamiliar_word"]=list(set(clicked_words))
    st.session_state["familiar_word"]=list(set(words)-set(clicked_words))
    with st.expander("Details",expanded=False):
      st.write(st.session_state["translation"])
      st.markdown(st.session_state["explanation"])
  
  col1,col2=st.columns(2,)
  with col1:
    if st.button("Next"):
      await st.session_state["vm_task"]  # Wait for the previous task to finish
      st.session_state["sentence"]=st.session_state["vm"].sentence
      st.session_state["translation"]=st.session_state["vm"].translation
      st.session_state["explanation"]=st.session_state["vm"].explanation
      st.session_state["vm_task"]=asyncio.create_task(update_and_generate(st.session_state["vm"],st.session_state["unfamiliar_word"],st.session_state["familiar_word"]))
      st.rerun()
  with col2:
    if st.button('Change Language Settings'):
      st.session_state['practice']=False
      st.session_state['language_setting']=True
      st.rerun()