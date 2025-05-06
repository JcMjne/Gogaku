from google.cloud import texttospeech
from google.cloud import texttospeech_v1
import pycountry
import json
import os

client=texttospeech.TextToSpeechClient()
voices=client.list_voices()
codes=sorted(set(lang.split('-')[0] for voice in voices.voices for lang in voice.language_codes))
names=[]
unknown_id=0
for code in codes:
  language_name=pycountry.languages.get(alpha_2=code)
  #language_display=language_name.name if language_name else "Unknown"
  if language_name:
    language_display=language_name.name
  else:
    language_display=f"Unknown-{unknown_id}"
    unknown_id+=1
  names.append(language_display)
# save the language codes and names to a json file
with open('language_codes.json', 'w') as f:
  json.dump(dict(zip(names,codes)), f, indent=2)
