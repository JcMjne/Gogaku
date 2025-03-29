from gogaku.gemma_handler import lm_studio
import os
from gogaku.vocab_manager.vocab_manager import Vocab_Manager

class Vocab_Manager_Gemma(Vocab_Manager):
  def generate_sentence(self):
    """
    Generate a sentence using the language model.
    """
    msg=[{'role': 'system', 'content': self.msg_sys},
         {'role': 'user', 'content': self.msg_user}]
    response=self.lm.get_response(msg)
    self.sentence=response.split('Sentence:')[1].split('Translation:')[0].strip()
    self.translation=response.split('Translation:')[1].split('Explanation:')[0].strip()
    self.explanation=response.split('Explanation:')[1].strip().split('Words:')[0].strip()
    new_words=response.split('Words:')[1].strip().split(',')
    self.new_words=[word.strip() for word in new_words]

  def update_setting(self,language,proficiency,local_url='http://127.0.0.1:1234',max_score=5,request='',db_dir='./vocab_data/'):
    self.new_words=[]
    self.language=language
    self.proficiency=proficiency
    self.db_dir=db_dir
    os.makedirs(self.db_dir,exist_ok=True)
    self.vocab_db_path=f'{self.db_dir}{self.language.replace(' ','_').lower()}.csv'

    #Set up language model handler
    self.lm=lm_studio.LM_Studio_Handler(local_url)
    self.max_score=max_score
    self.msg_sys_base=f"You are teaching {self.language} to students at the {self.proficiency} level."
    self.msg_sys=self.msg_sys_base
    self.msg_user_format=f"""
      Here is a list of words followed by their priority scores."""+"""

      {}"""+f"""

      Please create a natural sentence in {self.language} at the {self.proficiency} level.
      Use more higher score words whenever possible.
      You do not need to use all the words.
      Also, provide 5 new words at the {self.proficiency} level which are not in the provided list.
      
      The output must strictly follow this format:
        Sentence:<Generated sentence>
        Translation:<English translation of generated sentence>
        Explanation:<Grammatical details of each word>
        Words:<5 new words at the {self.proficiency} level which are not in the provided list, separated by commas>

      When generating new words, do not add any spaces after the comma.
      Do not include any information other than the generated sentence and its explanation
      In the Explanation section, describe word conjugations and meanings and so on, but do not mention scores.
      Generate just a single sentence that is useful in daily conversation.
      """+request
    self.load_score()
