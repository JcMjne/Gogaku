import json
from google.cloud import texttospeech
import pycountry

tts_client=texttospeech.TextToSpeechClient()

with open('./language_codes.json') as f:
  table_lang_code=json.load(f)

table_lang={}
for lang, spacy_dict in table_lang_code.items():
  table_lang[lang]={}
  table_lang[lang]['spacy']=spacy_dict
  table_lang[lang]['lang_code']=spacy_dict.split('_')[0]
  voices=tts_client.list_voices(language_code=table_lang[lang]['lang_code'])
  #table_lang[lang]['speaker_names']=[v.name for v in voices.voices]
  table_lang[lang]['speaker_names']={}
  for v in voices.voices:
    region=pycountry.countries.get(alpha_2=v.name.split('-')[1].upper()).name
    if region not in table_lang[lang]['speaker_names']:
      table_lang[lang]['speaker_names'][region]={}
    name=v.name
    gender=v.ssml_gender.name
    if gender not in table_lang[lang]['speaker_names'][region]:
      table_lang[lang]['speaker_names'][region][gender]=[]
    table_lang[lang]['speaker_names'][region][gender].append(name)
with open('./table_lang.json', 'w') as f:
  json.dump(table_lang, f, indent=4, ensure_ascii=False)