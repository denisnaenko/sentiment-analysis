import nltk
from pymorphy3 import MorphAnalyzer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
import re

nltk.download('stopwords')

morph = MorphAnalyzer()

# С помощью лемматизации, стематизации, pos-тегов нужно убрать из словаря и обработки этот снизу мусор
stop_words = stopwords.words("russian") + ['это', 'нибудь']
stop_words.remove('не')

punctuation_marks = ('!', ',', '(', ')', ':', '-', '+', '?', '.', '«', '»', ';', '–', '-', '…', '—',
                      '#', '&', '%', '*', '“', '”', '`', "'", '"',  '\\', '/')

map_tags = {"ADJF": "ADJ",
"ADJS": "ADJ",
"ADVB": "ADV",
"Apro": "DET",
"COMP": "ADJ",
"CONJ": "CCONJ",
"GRND": "VERB",
"INFN": "VERB",
"INTJ": "INTJ",
"NOUN": "NOUN",
"NPRO": "PRON",
"NUMR": "NUM",
"NUMB": "NUM",
"PNCT": "PUNCT",
"PRCL": "PART",
"PREP": "ADP",
"PRTF": "VERB",
"PRTS": "VERB",
"VERB": "VERB",}

forbidden_tags = {'ADV', 'DET', 'CCONJ', 'INTJ', 'PRON', "PART", 'PUNCT', 'ADP'}


def remove_emoji(text):
  emoji_pattern = re.compile("["
                             u"\U0001F600-\U0001F64F"  # эмодзи эмоций
                             u"\U0001F300-\U0001F5FF"  # символы и пиктограммы
                             u"\U0001F680-\U0001F6FF"  # эмодзи транспорта
                             u"\U0001F1E0-\U0001F1FF"  # эмодзи флагов стран
                             u"\U00002500-\U00002BEF"  # китайские иероглифы
                             u"\U00002702-\U000027B0"
                             u"\U00002702-\U000027B0"
                             u"\U000024C2-\U0001F251"
                             u"\U0001f926-\U0001f937"
                             u"\U00010000-\U0010ffff"
                             u"\u2640-\u2642"
                             u"\u2600-\u2B55"
                             u"\u200d"
                             u"\u23cf"
                             u"\u23e9"
                             u"\u231a"
                             u"\ufe0f"  # variation selector
                             u"\u3030"
                             "]+", flags=re.UNICODE)
  return emoji_pattern.sub(r'', text)

def preprocess(text, stop_words, punctuation_marks, morph):
  """Разбивка предложений на слова"""
  text = str(text).lower()
  # Удаление эмодзи
  text = remove_emoji(text)
  # Удаление пунктуации
  for letter in punctuation_marks:
    text = text.replace(letter, ' ')

  tokens = word_tokenize(text)
  preprocessed_text = []
  for token in tokens:
    if len(token) > 1:
      lemma = morph.parse(token)[0].normal_form
      if lemma not in stop_words:
        preprocessed_text.append(lemma)
  return preprocessed_text

def replace_keys_with_values(data, dictionary):
  result = []
  for item in data:
    if item in dictionary:
      result.append(dictionary[item])
    else:
      result.append(item)  # Если ключ не найден в словаре, оставляем исходное значение
  return result

def extract_keywords_phrases(text):

  # 1. Предобработка текста

  # Токенизация и удаление стоп-слов
  lemmas = preprocess(text, stop_words, punctuation_marks, morph)

  # POS-тэггинг
  pos_tags = [morph.parse(word)[0].tag.POS for word in lemmas]
  pos_tags = replace_keys_with_values(pos_tags, map_tags)

  # 2. Извлечение ключевых слов

  # TF-IDF для ключевых слов
  vectorizer = TfidfVectorizer()
  tfidf_matrix = vectorizer.fit_transform(lemmas)
  word_scores = tfidf_matrix.sum(axis=0)
  sorted_indices = word_scores.argsort()[::-1]
  keywords = [vectorizer.get_feature_names_out()[i] for i in sorted_indices[:10]]

  # 3. Извлечение ключевых фраз

  # Создание n-грамм (фразы из 2-3 слов)
  ngrams = []
  for i in range(len(lemmas) - 1):
    ngrams.append(' '.join(lemmas[i:i+2]))
  for i in range(len(lemmas) - 2):
    ngrams.append(' '.join(lemmas[i:i+3]))

  # TF-IDF для ключевых фраз
  vectorizer = TfidfVectorizer(ngram_range=(2, 3))
  tfidf_matrix = vectorizer.fit_transform(ngrams)
  phrase_scores = tfidf_matrix.sum(axis=0)
  sorted_indices = phrase_scores.argsort()[::-1]
  keyphrases = [vectorizer.get_feature_names_out()[i] for i in sorted_indices[:10]]

  filtered_keyphrases = []
  # 4. Фильтрация по POS-тэгам (исключаем глаголы)
  filtered_keywords = [lemmas[i] for i in range(len(pos_tags)) if pos_tags[i] == 'NOUN']
  for phrase in keyphrases:
    for words in phrase[0]:
      words1 = words.split()
      pos_tags1 = [morph.parse(word)[0].tag.POS for word in words1]
      pos_tags1 = replace_keys_with_values(pos_tags1, map_tags)
      if not any(tag in forbidden_tags for tag in pos_tags1):
        filtered_keyphrases.append(words)

  data_dict = {'keyphrases': filtered_keyphrases[:10]}


  return data_dict




