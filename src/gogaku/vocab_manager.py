import numpy as np
from gogaku.gemma_handler import lm_studio
import os

class Vocab_Manager:
  def __init__(self):
    pass
  
  def generate_sentence(self):
    """
    Generate a sentence using the language model.
    """
    msg=[{'role': 'system', 'content': self.msg_sys},
         {'role': 'user', 'content': self.msg_user}]
    response=self.lm.get_response(msg)
    self.sentence=response.split('Sentence: ')[1].split('Translation: ')[0]
    self.translation=response.split('Translation: ')[1].split('Explanation: ')[0]
    self.explanation=response.split('Explanation: ')[1]

  def generate_sentence_test(self):
    """
    Test function to generate a sentence using the language model.
    """
    idx=np.random.randint(0,10**4)
    self.sentence=f'This is the generated {self.language} sentence (id: {idx})'
    self.translation=f'This is the translation of the generated {self.language} sentence (id: {idx})'
    self.explanation=f'This is the explanation of the generated {self.language} sentence (id: {idx})'
  
  def load_score(self):
    """
    Load the words and their proficiency scores.
    """
    data=np.loadtxt(self.vocab_db_path,delimiter=",", dtype=str)
    self.words=data[:,0]
    self.scores=data[:,1].astype(int)

    #Select words with proficiency score less than self.max_score
    idx_learning=np.where(self.scores<self.max_score)[0]
    self.word_learning=self.words[idx_learning]
    self.score_leaning=self.scores[idx_learning]
    msg=[f"{self.word_learning[i]}: {self.score_leaning[i]}, " for i in range(len(idx_learning))]
    self.msg_user=self.msg_user_format.format("".join(msg))

  def save_score(self):
    """
    Save the words and their proficiency scores.
    """
    np.savetxt(self.vocab_db_path,np.column_stack([self.words,self.scores]),delimiter=",",fmt="%s")

  def update_score(self,unfamiliar_words,familiar_words):
    """
    Update the proficiency scores of the words.
    Add words to the database if they are not already present.
    """
    if len(unfamiliar_words)==0:
      return
    word_dict={word:score for word,score in zip(self.words,self.scores)}
    for word in unfamiliar_words:
      if word in word_dict:
        word_dict[word]=max(word_dict[word]-1,0)
      else:
        word_dict[word]=0
    for word in familiar_words:
      if word in word_dict:
        word_dict[word]=min(word_dict[word]+1,self.max_score)
      else:
        word_dict[word]=self.max_score-1

    self.words=np.array(list(word_dict.keys()))
    self.scores=np.array(list(word_dict.values()))
    self.save_score()

    #Select words with proficiency score less than self.max_score
    idx_learning=np.where(self.scores<self.max_score)[0]
    self.word_learning=self.words[idx_learning]
    self.score_leaning=self.scores[idx_learning]
    msg=[f"{self.word_learning[i]}: {self.score_leaning[i]}, " for i in range(len(idx_learning))]
    self.msg_user=self.msg_user_format.format("".join(msg))
    
  def update_setting(self,language='Italian',proficiency='A1',local_url='http://127.0.0.1:1234',max_score=5):
    self.language=language
    self.proficiency=proficiency
    self.db_dir=f'./vocab_data/'
    os.makedirs(self.db_dir,exist_ok=True)
    self.vocab_db_path=f'{self.db_dir}{self.language.lower()}.csv'

    #Set up language model handler
    self.lm=lm_studio.LM_Studio_Handler(local_url)
    self.max_score=max_score
    self.msg_sys_base=f"You are a professional {self.language} language tutor, teaching students at the {self.proficiency} level."
    self.msg_sys=self.msg_sys_base
    self.msg_user_format=f"""
      Here is a list of words followed by their proficiency scores on a scale from 0 to {self.max_score},\
        where 0 represents the lowest proficiency level and {self.max_score} represents the highest."""+"""

      {}"""+f"""

      Please create natural {self.language} sentences using as many words as possible from the list above. 
      Prioritize words with lower proficiency scores while keeping the sentences natural.

      The output should follow this format:
        Sentences: <Generated sentences>
        Translation: <English translation of generated sentences>
        Explanation: <Grammatical explanation of the sentences>

      Do not include anything other than the requested output.
      """
