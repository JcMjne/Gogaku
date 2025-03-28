#gogalu/gemma_handler/lm_studio.py

import requests, json

local_url='http://127.0.0.1:1234'

class LM_Studio_Handler:
  """
  Interact with the LM Studio API.
  """
  def __init__(self, url=local_url):
    self.url=url
    response=requests.get(f'{self.url}/v1/models')
    models=json.loads(response.text)
    self.modelname= models['data'][0]['id']

  def get_response(self,msg):
    """
    Get response from the model.
    """
    data={'model':self.modelname,'messages':msg}
    response=requests.post(f'{self.url}/v1/chat/completions',json=data)
    response_content = json.loads(response.text)
    response_text=response_content['choices'][0]['message']['content']
    return response_text