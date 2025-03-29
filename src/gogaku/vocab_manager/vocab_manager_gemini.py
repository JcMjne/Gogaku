from gogaku.vocab_manager.vocab_manager import Vocab_Manager
import os
from google.genai import types
import streamlit as st

class Vocab_Manager_Gemini(Vocab_Manager):
  def generate_sentence(self):
    """
    Generate a sentence using the language model.
    """
    response=st.session_state['gemini_client'].models.generate_content(
      model=st.session_state['current_model'],
      config=types.GenerateContentConfig(
        temperature=st.session_state['gemini_temperature'],
        system_instruction=self.msg_sys),
      contents=self.msg_user).text
    self.sentence=response.split('Sentence:')[1].split('Translation:')[0].strip()
    self.translation=response.split('Translation:')[1].split('Explanation:')[0].strip()
    self.explanation=response.split('Explanation:')[1].strip().split('Words:')[0].strip()
    new_words=response.split('Words:')[1].strip().split(',')
    self.new_words=[word.strip() for word in new_words]+st.session_state['additional_words']
    st.session_state['additional_words']=[]
    
  def update_setting(self,language,proficiency,max_score=5,request='',db_dir='./vocab_data/'):
    self.new_words=[]
    self.language=language
    self.proficiency=proficiency
    self.db_dir=db_dir
    os.makedirs(self.db_dir,exist_ok=True)
    self.vocab_db_path=f'{self.db_dir}{self.language.replace(' ','_').lower()}.csv'
    self.max_score=max_score
    self.msg_sys=f"""You are teaching {self.language} to students at the {self.proficiency} level. \
      Follow the user's instructions carefully and generate a sentence in {self.language} that aligns with the provided words and priorities. \
        Provide explanations and additional words as specified, without mentioning the priority scores. \
          Even if the target language does not use space between words normally, put spaces between words in the generated sentence. \
            The generated sentence should be useful in daily conversation.\
              All the translations and explanations must be done in {st.session_state['user_language']}. \
              The content of the explanations should also be suitable for the {self.proficiency} level. \
                Omit the explanation of easy words for the {self.proficiency} level."""
              
    self.msg_user_format=f"""
      Here is a list of words followed by their priority scores."""+"""

      {}"""+f"""

      Please create a natural sentence in {self.language} at the {self.proficiency} level.
      Use more higher score words whenever possible.
      You do not need to use all the words.
      Also, provide 5 new words at the {self.proficiency} level which are not in the provided list.
      
      The output must strictly follow this format:
        Sentence:<Generated sentence>
        Translation:<Translation of generated sentence>
        Explanation:<Detailed grammatical explanation>
        Words:<5 new words at the {self.proficiency} level which are not in the provided list, separated by commas>

      When generating new words, do not add any spaces after the comma.
      In the Explanation section, describe word conjugations and meanings and so on in list format, but do not mention scores.
      """+request
    self.load_score()
