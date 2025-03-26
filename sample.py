import streamlit as st
import numpy as np
import requests,json,os

def get_first_words(language:str,level:str):
  url=st.session_state['url']
  response = requests.get(f'{url}/v1/models')
  model=json.loads(response.text)['data'][0]['id']
  msg=f"""Generate 10 {language.title()} words at the {level} level in the following format:
  <word 1>,<word 2>,...,<word 10>
  Do not say anything else."""
  data={'model':model,'messages':[{'role':'user','content':msg}]}
  response = requests.post(f'{url}/v1/chat/completions', json=data)
  response_content = json.loads(response.text)
  raw_text=response_content['choices'][0]['message']['content']
  text=raw_text.replace('<','').replace('>','').split(',')
  if len(text)!=10:
    st.error("Error occurred in generating words.")
  st.write(f"First 10 words in {language.title()} at the {level} level are:",*text)
  if not os.path.exists(st.session_state['db_dir']+f'{language.lower().replace(' ','_')}.csv'):
    np.savetxt(st.session_state['db_dir']+f'{language.lower().replace(' ','_')}.csv',np.column_stack([text,np.zeros(10,int)]),fmt='%s',delimiter=',',encoding='utf-8')
  
def initial_settings():
  if 'language' not in st.session_state:
    st.session_state['language']=[]
    st.session_state['proficiency']={}
  if 'db_dir' not in st.session_state:
    st.session_state['db_dir']='./vocab_data/'
  st.session_state['url']='http://127.0.0.1:1234'

  st.title("Language Settings")
  if len(st.session_state['language'])>0:
    data=[f"{lang.title()} ({proficiency})," for lang,proficiency in st.session_state['proficiency'].items()]
    st.write('You are learning ',*data)

  language=st.text_input("Type the name of the language you want to learn in English.",placeholder='English').lower()
  levels=["A1","A2","B1","B2","C1","C2"]
  proficiency = st.selectbox("Select your level.",levels)
  
  if st.button("Confirm"):
    if language in st.session_state['language']:
      st.success("Language settings updated.")

    elif len(language)!=0:
      st.session_state['language'].append(language)
      st.session_state['proficiency'][language]=proficiency
      st.success("Language added.")
      if not os.path.exists(st.session_state['db_dir']+f'{language.lower()}.csv'):
        get_first_words(language,proficiency)
  st.write("The language you want to learn is:",*st.session_state['language'])
  st.write("Your proficiency level is:",proficiency)

if __name__ == "__main__":
  initial_settings()