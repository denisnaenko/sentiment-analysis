import nltk
from pymorphy3 import MorphAnalyzer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

morph = MorphAnalyzer()

# С помощью лемматизации, стематизации, pos-тегов нужно убрать из словаря и обработки этот снизу мусор
stop_words = stopwords.words("russian") + ['это', 'аж', 'ка', 'мя', 'ул', 'ом', 'ма', 'ый', 'мр', 'тр', 'чей',
                                           'сгс', 'ля', 'эппл', 'юсб', 'тлф', 'ася', 'азс', 'ик', 'нуть', 'юрий',
                                           'тат', 'эл', 'ух', 'джи', 'дог', 'грн', 'ия', 'изз', 'самс', 'дак', 'пвз',
                                           'ке', 'ин', 'гпс', 'сап', 'аля', 'хны', 'эх', 'зы']
stop_words.remove('не')

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

forbidden_tags = {'ADV', 'DET', 'CCONJ', 'INTJ', 'PRON', 'PUNCT', 'PART', 'ADP'}

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
  tokens = nltk.word_tokenize(text)
  tokens = [token.lower() for token in tokens if token.lower() not in stop_words]

  # Лемматизация
  lemmas = [morph.parse(token)[0].normal_form for token in tokens]

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

  return filtered_keywords, filtered_keyphrases

# Пример использования
text = "Заказывала 2 былых панели.Пришли одна серая, другая светлокоричневая. У одной уже немного треснута рейка. Явно панели ездят от покупателя к покупателю давно, т.к. упаковка вся сто раз заклеена переклеена.Недобросовестный продавец отправляет их туда-сюда, авось кто-нибудь возьмет. Мне вместо белых пришло что попало"

keywords, keyphrases = extract_keywords_phrases(text)
print(f"Ключевые слова: {keywords}")
print(f"Ключевые фразы: {keyphrases}")


