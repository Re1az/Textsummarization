# nltk_setup.py
import nltk

def ensure_nltk_resources():
    required = ['averaged_perceptron_tagger_eng']
    for resource in required:
        try:
            nltk.data.find(f'taggers/{resource}')
        except LookupError:
            nltk.download(resource)
