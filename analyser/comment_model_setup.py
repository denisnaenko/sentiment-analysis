import joblib, json, re
from numpy import zeros
from string import ascii_lowercase
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from pymorphy3 import MorphAnalyzer
from collections import Counter

# константы
max_words = 10000
random_state = 42

punctuation_marks = ('!', ',', '(', ')', ':', '-', '+', '?', '.', '«', '»', ';', '–', '-', '…', '—',
                      '#', '&', '%', '*', '“', '”', '`', "'", '"', '0', '1', '2', '3', '4', '5', '6', '7', '8',
                      '9', '\\', '/') + tuple(ascii_lowercase)

# С помощью лемматизации, стематизации, pos-тегов нужно убрать из словаря и обработки этот снизу мусор
stop_words = stopwords.words("russian") + ['это', 'нибудь']
stop_words.remove('не')

morph = MorphAnalyzer()

# загрузка модели
with open('analyser/models/comment_analysis_model.joblib', 'rb') as file:
    model = joblib.load(file)

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

words = Counter()

# словарь, отображающий слова в коды
word_to_index = dict()

# создаем словарь
for i, word in enumerate(words.most_common(max_words - 2)):
    word_to_index[word[0]] = i + 2

# открываем файл и заполняем словарь word_to_index данными
with open('analyser/data_dictionaries/comments_dictionary.json', 'r') as file:
    data = json.load(file)
    word_to_index.update(eval(str(data)))

# функция для преобразования списка слов в список кодов
def text_to_sequence(txt, word_to_index):
    seq = []
    for word in txt:
        index = word_to_index.get(word, 1) # 1 означает неизвестное слово
        # Неизвестные слова не добавляем в выходную последовательность
        if index != 1:
            seq.append(index)
    return seq

def bag_of_words_from_column(column, dimension):
    sequences = column.tolist()

    words_counter = Counter()

    for seq in sequences:
        words_counter.update(seq)

    most_common_words = [word for word, _ in words_counter.most_common(dimension)]
    word_to_idx = {word: idx for idx, word in enumerate(most_common_words)}

    bag_of_words = zeros((len(sequences), dimension))

    for i, seq in enumerate(sequences):
        for word in seq:
            if word in word_to_idx:
                bag_of_words[i, word_to_idx[word]] += 1

    return bag_of_words

def vectorize_sequences(sequences, dimension=10000):
    results = zeros((len(sequences), dimension))
    for i, sequence in enumerate(sequences):
        for index in sequence:
            results[i, index] += 1.
    return results

def analyse_sentiment(comment):
    comment_preprocessed_text = preprocess(comment, stop_words, punctuation_marks, morph)
    comment_seq = text_to_sequence(comment_preprocessed_text, word_to_index)
    comment_bow = vectorize_sequences([comment_seq])
    sentiment = model.predict(comment_bow)
    sentiment_stats = model.predict_proba(comment_bow)

    sentiment_dict = {}

    if sentiment == 0: sentiment_dict['sentiment'] = 'Негативный'
    elif sentiment == 1: sentiment_dict['sentiment'] = 'Нейтральный'
    elif sentiment == 2: sentiment_dict['sentiment'] = 'Позитивный'

    sentiment_dict['negativity_rate'] = f"{round(sentiment_stats[0][0], 2) * 100}%"
    sentiment_dict['neutrality_rate'] = f"{round(sentiment_stats[0][1], 2) * 100}%"
    sentiment_dict['positivity_rate'] = f"{round(sentiment_stats[0][2], 2) * 100}%"

    return sentiment_dict
