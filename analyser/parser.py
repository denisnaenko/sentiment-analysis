from selenium import webdriver
from selenium.webdriver.common.by import By
from fake_useragent import UserAgent
from time import sleep
import datetime, csv

def get_data(article):
    # useragent
    useragent = UserAgent()

    # options
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={useragent.random}")
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--headless')

    start_time = datetime.datetime.now()
    driver = webdriver.Chrome(options=options)
    csv_filename = f'feedback_data_{article}.csv'

    with open(csv_filename, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(('Comment', 'Rating'))

    try:
        driver.get(f"https://www.wildberries.ru/catalog/{article}/feedbacks")
        print("\nthe page has loaded...")

        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        match = False
        while not match:
            lastCount = lenOfPage
            sleep(2)
            lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
            if lastCount == lenOfPage:
                match = True
        print('the page has scrolled to the bottom...')

        all_comments = driver.find_elements(By.CLASS_NAME, 'feedback__text')
        all_ratings_class = driver.find_elements(By.CLASS_NAME, 'feedback__rating')
        all_ratings_value = []

        for value in all_ratings_class:
            grade = value.get_attribute('class')
            all_ratings_value.append(grade[-1])
        print('data has been collected...')

        feedback_data_dict = {'comments': [comments.text for comments in all_comments],
                              'rating': all_ratings_value}

        total_feedback = len(all_comments)

        for feedback_num in range(total_feedback):
            comment = feedback_data_dict['comments'][feedback_num]
            rating = feedback_data_dict['rating'][feedback_num]

            with open(csv_filename, 'a', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow((comment, rating))
        print('csv-file has been formed...')

    except Exception as ex:
        print(ex)

    finally:
        driver.close()
        driver.quit()

    # Проверка на наличие отзывов в CSV-файле
    with open(csv_filename, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        row_count = sum(1 for row in file)

    runtime = datetime.datetime.now() - start_time
    print(f"\truntime: {runtime}")

    if row_count > 2: return True
    else: return False

