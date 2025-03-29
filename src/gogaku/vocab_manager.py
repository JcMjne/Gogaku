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
    self.sentence=response.split('Sentence:')[1].split('Translation:')[0].strip()
    self.translation=response.split('Translation:')[1].split('Explanation:')[0].strip()
    self.explanation=response.split('Explanation:')[1].strip().split('Words:')[0].strip()
    new_words=response.split('Words:')[1].strip().split(',')
    self.new_words=[word.strip() for word in new_words]

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
    data=np.loadtxt(self.vocab_db_path,delimiter=",",dtype=str,encoding='utf-8')
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
    np.savetxt(self.vocab_db_path,np.column_stack([self.words,self.scores]),delimiter=",",fmt="%s",encoding='utf-8')

  def update_score(self,unfamiliar_words,familiar_words):
    """
    Update the proficiency scores of the words.
    Add words to the database if they are not already present.
    """
    word_dict={word:score for word,score in zip(self.words,self.scores)}
    unfamiliar_words=[word.lower() for word in unfamiliar_words]+self.new_words
    unfamiliar_words=list(set(unfamiliar_words))
    familiar_words=[word.lower() for word in familiar_words]
    for word in unfamiliar_words:
      if word in word_dict:
        word_dict[word]=max(word_dict[word]-1,0)
      else:
        word_dict[word]=0
    for word in familiar_words:
      if word in word_dict:
        word_dict[word]=min(word_dict[word]+1,self.max_score)

    self.words=np.array(list(word_dict.keys()))
    self.scores=np.array(list(word_dict.values()))
    self.save_score()

    #Select words with proficiency score less than self.max_score
    idx_learning=np.where(self.scores<self.max_score)[0]
    self.word_learning=self.words[idx_learning]
    self.score_leaning=self.scores[idx_learning]
    idx=np.arange(len(self.word_learning))
    np.random.shuffle(idx)
    msg=[f"{self.word_learning[idx[i]]}: {self.max_score-self.score_leaning[idx[i]]}, " for i in range(len(idx_learning))]
    self.msg_user=self.msg_user_format.format("".join(msg))
    
  def update_setting(self,language='Italian',proficiency='A1',local_url='http://127.0.0.1:1234',max_score=5,request='',db_dir='./vocab_data/'):
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
