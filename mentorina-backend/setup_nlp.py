import spacy
import json

with open('./data/table_lang.json') as f:
  table_lang = json.load(f)

def download_model():
  for lang in table_lang:
    spacy.cli.download(table_lang[lang]['spacy'])

def get_nlps():
  nlp_dict={}
  for lang in table_lang:
    nlp_dict[lang]=spacy.load(table_lang[lang]['spacy'])
  return nlp_dict

if __name__ == "__main__":
  download_model()