from gogaku.gemma_handler import lm_studio
from gogaku.vocab_manager import Vocab_Manager
import os

class Vocab_Manager_JP(Vocab_Manager):
  def update_setting(self,language='Italian',proficiency='A1',local_url='http://127.0.0.1:1234',max_score=5,request='',db_dir=f'./vocab_data/'):
    self.new_words=[]
    self.language=language
    self.proficiency=proficiency
    self.db_dir=db_dir
    os.makedirs(self.db_dir,exist_ok=True)
    self.vocab_db_path=f'{self.db_dir}{self.language.replace(' ','_').lower()}.csv'

    #Set up language model handler
    self.lm=lm_studio.LM_Studio_Handler(local_url)
    self.max_score=max_score
    self.msg_sys_base=f"あなたは{self.language}を{self.proficiency}レベルの生徒に教えています。"
    self.msg_sys=self.msg_sys_base
    self.msg_user_format=f"""
      以下は、0から{self.max_score}までのスケールで評価された単語のリストです。"""+"""

      {}"""+f"""

      スコアの大きな単語を多く使用しつつ、{self.language}で{self.proficiency}レベルの文を作成してください。
      生成する文は一文のみです。
      自然な表現、文脈になることを最優先してください。
      すべての単語を使用する必要はありません。
      さらに単語リストに含まれていない{self.proficiency}レベルの単語を5個提供してください。
      出力は次の形式に厳密に従ってください。
        Sentence:<Generated sentence>
        Translation:<Japanese translation of generated sentence>
        Explanation:<Grammatical details of each word>
        Words:<5 new words at the {self.proficiency} level which are not in the provided list, separated by commas>

      生成された文以外の情報は含めないでください。
      Explanationでは、活用や単語の意味について日本語で説明し、スコアについては触れないでください。
      Sentence、Translation、Explanationの各項目は一回ずつのみ生成してください。
      新しい単語の生成ではカンマの後にスペースを入れないでください。
      """+request
    self.load_score()
