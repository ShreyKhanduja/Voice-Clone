# -*- coding: utf-8 -*-
"""VoiceClone.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1I83EcegQ555yOi0Sx1ilDn1hDd6qGymN

Step 1: Install Basic Dependencies
"""

# Commented out IPython magic to ensure Python compatibility.
!pip3 install -U scipy

!git clone https://github.com/jnordberg/tortoise-tts.git
# %cd tortoise-tts
!pip3 install -r requirements.txt
!pip3 install transformers==4.19.0 einops==0.5.0 rotary_embedding_torch==0.1.5 unidecode==1.3.5
!python3 setup.py install

import torch
import torchaudio
import torch.nn as nn
import torch.nn.functional as F

import IPython

from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio, load_voice, load_voices

tts = TextToSpeech()

import os
from google.colab import files

"""Step 2: Install library to **extract Text from Wav**"""

!pip3 install SpeechRecognition pydub

"""Step 3: **Extract Text from Wav**"""

import speech_recognition as sr
filename = "/content/original_audio.wav"
r = sr.Recognizer()
# open the file
with sr.AudioFile(filename) as source:
    # listen for the data (load audio to memory)
    audio_data = r.record(source)
    # recognize (convert from speech to text)
    original_text = r.recognize_google(audio_data)
    print(original_text)

"""Step 4: Install library to **Translate English to Hindi**"""

!pip install gtts googletrans==4.0.0-rc1

"""Step 5: **Translate English to Hindi**"""

from gtts import gTTS
from googletrans import Translator
original_language = "en"
target_language = "hi"
translator = Translator()
translated_text = translator.translate(original_text, src=original_language, dest=target_language).text
print(translated_text)

"""Step 6: Install library to **Convert Devnagri script to Roman script**"""

!pip install indic-transliteration

"""Step 7: **Convert Devnagri script to Roman script**"""

from indic_transliteration import sanscript

def devanagari_to_roman(text):
    # Transliterate Devanagari script to Roman script using ITRANS scheme
    roman_text = sanscript.transliterate(text, sanscript.DEVANAGARI, sanscript.ITRANS)

    return roman_text

# Example usage:
roman_text = devanagari_to_roman(translated_text)
print("Devanagari:", translated_text)
print("Roman:", roman_text)

"""Step 8: **Choose Preset and Upload the training file**"""

# choose a "preset mode" to determine quality. Options: {"ultra_fast", "fast" (default), "standard", "high_quality"}.
preset = "high_quality"

CUSTOM_VOICE_NAME = "obama_HighQuality"

custom_voice_folder = f"tortoise/voices/{CUSTOM_VOICE_NAME}"
os.makedirs(custom_voice_folder)
for i, file_data in enumerate(files.upload().values()):
  with open(os.path.join(custom_voice_folder, f'{i}.wav'), 'wb') as f:
    f.write(file_data)

"""Step 9: **Print text in Devnagri and Roman scripts for our reference**"""

print(translated_text)
print(roman_text)

"""Step 10: **Generate Cloned Voice**"""

# Generate speech
max_text_length = 200  # Set an appropriate maximum text length
text_segments = [roman_text[i:i+max_text_length] for i in range(0, len(roman_text), max_text_length)]

# Load voice samples and conditioning latents
voice_samples, conditioning_latents = load_voice(CUSTOM_VOICE_NAME)

# Initialize an empty tensor to accumulate the generated audio
gen_audio = torch.Tensor()

# Process each text segment separately
for segment in text_segments:
    # Preprocess the segment if needed
    segment = (segment.translate({ord(i): None for i in 'M'})).lower()

    # Generate audio for the current segment
    gen_segment = tts.tts_with_preset(segment, voice_samples=voice_samples, conditioning_latents=conditioning_latents, preset=preset)

    # Accumulate the generated audio
    gen_audio = torch.cat((gen_audio, gen_segment.squeeze(0)), dim=-1)

# Save the final generated audio
torchaudio.save(f'generated-{CUSTOM_VOICE_NAME}.wav', gen_audio.cpu(), 24000)

# Display the audio
IPython.display.Audio(f'generated-{CUSTOM_VOICE_NAME}.wav')

print(translated_text)
print(roman_text)