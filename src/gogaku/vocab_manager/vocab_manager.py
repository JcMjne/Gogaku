import numpy as np
import datetime

class Vocab_Manager:
  def __init__(self):
    pass
  
  def generate_sentence(self):
    """
    Generate a sentence using the language model.
    """
    pass

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
    data=np.loadtxt(self.vocab_db_path,delimiter=",",dtype=str,encoding='utf-16')
    self.words=data[:,0]
    self.scores=data[:,1].astype(int)
    self.timestamps = data[:, 2]
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    #Select words with proficiency score less than self.max_score
    idx_learning=np.where((self.scores<self.max_score)*(self.timestamps<current_time))[0]
    self.word_learning=self.words[idx_learning]
    self.score_leaning=self.scores[idx_learning]
    self.timestamp_learning = self.timestamps[idx_learning]
    msg=[f"{self.word_learning[i]}: {self.max_score-self.score_leaning[i]}, " for i in range(len(idx_learning))]
    self.msg_user=self.msg_user_format.format("".join(msg))

  def save_score(self):
    """
    Save the words and their proficiency scores.
    """
    np.savetxt(self.vocab_db_path,np.column_stack([self.words,self.scores,self.timestamps]),delimiter=",",fmt="%s",encoding='utf-16')

  def update_score(self,unfamiliar_words,familiar_words):
    """
    Update the proficiency scores of the words.
    Add words to the database if they are not already present.
    """
    word_dict_score={word:score for word,score in zip(self.words,self.scores)}
    word_dict_timestamp={word:timestamp for word,timestamp in zip(self.words,self.timestamps)}
    unfamiliar_words=[word.lower() for word in unfamiliar_words]+self.new_words
    unfamiliar_words=list(set(unfamiliar_words))
    familiar_words=[word.lower() for word in familiar_words]
    for word in unfamiliar_words:
      if word in word_dict_score:
        new_score=max(word_dict_score[word]-1,0)
        word_dict_score[word]=new_score
        word_dict_timestamp[word]=(datetime.datetime.now()+datetime.timedelta(minutes=5*(int(new_score)+1)**2)).strftime('%Y-%m-%d %H:%M:%S')
      else:
        word_dict_score[word]=0
        word_dict_timestamp[word]=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for word in familiar_words:
      if word in word_dict_score:
        new_score=min(word_dict_score[word]+1,self.max_score)
        word_dict_score[word]=new_score
        word_dict_timestamp[word]=(datetime.datetime.now()+datetime.timedelta(minutes=10*(int(new_score)+1)**3)).strftime('%Y-%m-%d %H:%M:%S')

    self.words=np.array(list(word_dict_score.keys()))
    self.scores=np.array(list(word_dict_score.values()))
    self.timestamps=np.array(list(word_dict_timestamp.values()))
    self.save_score()
    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #Select words with proficiency score less than self.max_score
    idx_learning=np.where((self.scores<self.max_score)*((self.timestamps<current_time)))[0]
    self.word_learning=self.words[idx_learning]
    self.score_leaning=self.scores[idx_learning]
    idx=np.arange(len(self.word_learning))
    np.random.shuffle(idx)
    print(idx.shape)
    msg=[f"{self.word_learning[idx[i]]}: {self.max_score-self.score_leaning[idx[i]]}, " for i in range(len(idx_learning))]
    self.msg_user=self.msg_user_format.format("".join(msg))
    
  def update_setting(self):
    pass

  
