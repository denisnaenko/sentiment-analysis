import pandas as pd

# Создаем пустой DataFrame для объединения данных
FILE_NAME = 'Телефоны'
all_data = pd.read_csv(f'{FILE_NAME}.csv', sep=',')
all_data = all_data[['Text', 'Score', 'Sequences', 'Preprocessed_texts']]
mapping = {"1": 0, "2": 0, "3": 1, "4": 2, "5": 2}
all_data.replace({'Score': mapping}, inplace=True)

# Цикл по всем файлам с названиями "1.csv", "2.csv", ..., "50.csv"
names = ['wb-обраб', 'Yandex-1-обраб', 'Yandex-2-обраб', 'Yandex-31-обраб', 'Yandex-32-обраб']
for number_csv in names:
    # Загружаем данные из текущего файла, пропуская заголовок и используя собственные заголовки
    data = pd.read_csv(f'{number_csv}.csv')

    data = data[['Text', 'Score', 'Sequences', 'Preprocessed_texts']]

    all_data = pd.concat([all_data, data])  # Объединяем данные в один DataFrame

all_data.reset_index(drop=True)
# Сохраняем объединенные данные в новый файл с заголовками "idx", "Score", "text"
all_data.to_csv('Yandex, wb, телефоны Собранный.csv', index_label='Index')