import streamlit as st
import re

def update_and_generate(vm,unfamiliar_words=None,familiar_words=None):
  if (unfamiliar_words is not None) or (familiar_words is not None):
    vm.update_score(unfamiliar_words,familiar_words)
  vm.generate_sentence()

def main_page():
  st.title(f"Practice {st.session_state['current_language']}!")
  if "unfamiliar_word" not in st.session_state:
    st.session_state["unfamiliar_word"]=None
    st.session_state["familiar_word"]=None
  if "sentence" not in st.session_state:
    update_and_generate(st.session_state["vm"],st.session_state["unfamiliar_word"],st.session_state["familiar_word"])
    st.session_state["sentence"]=st.session_state["vm"].sentence
    st.session_state["translation"]=st.session_state["vm"].translation
    st.session_state["explanation"]=st.session_state["vm"].explanation
    
  if "sentence" in st.session_state:
    st.subheader(st.session_state["sentence"])
    words=re.sub(r'[^\w\s\']', '', st.session_state["sentence"]).split(' ')
    words= [word for word in words if len(word) > 0]
    clicked_words=st.pills("Click the words you don't understand.", words,selection_mode="multi")
    st.session_state["unfamiliar_word"]=list(set(clicked_words))
    st.session_state["familiar_word"]=list(set(words)-set(clicked_words))
    with st.expander("Details",expanded=False):
      st.write(st.session_state["translation"])
      st.markdown(st.session_state["explanation"])
  
  col1,col2=st.columns(2,)
  with col1:
    if st.button("Next"):
      del st.session_state["sentence"]
      st.rerun()
  with col2:
    if st.button('Change Language Settings'):
      st.session_state['practice']=False
      st.session_state['language_setting']=True
      st.rerun()