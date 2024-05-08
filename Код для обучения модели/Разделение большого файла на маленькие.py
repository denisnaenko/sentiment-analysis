import pandas as pd

FILE_NAME = 'wb'
reviews = pd.read_csv(f'{FILE_NAME}.csv', sep=',')
# Нужны только "Текст" и "Оценка тональности"
reviews = reviews[['Text', 'Score']]
reviews.reset_index(drop=True)

# Количество строк данных в каждом файле
chunk_size = 164000 // 2
# Кол-во новых файлов
num_chunks = 2

# Разделение большого файла на маленькие
for column in reviews.columns:
    for i in range(num_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(reviews))

        chunk = reviews.iloc[start:end]
        chunk.to_csv(f'{FILE_NAME}-{i+1}.csv')

print('Файлы успешно разделены!')



