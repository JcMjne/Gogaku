from google.cloud import texttospeech

def synthesize_text(client,text,language_code,name):
  """Synthesizes speech from the input string of text."""
  input_text=texttospeech.SynthesisInput(text=text)

  # Note: the voice can also be specified by name.
  # Names of voices can be retrieved with client.list_voices().
  voice=texttospeech.VoiceSelectionParams(
    language_code=language_code,
    name=name,
  )

  audio_config=texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
  )

  response=client.synthesize_speech(
    input=input_text,
    voice=voice,
    audio_config=audio_config,
  )

  # The response's audio_content is binary.
  with open("text_audio.mp3", "wb") as out:
    out.write(response.audio_content)
  return response.audio_content
