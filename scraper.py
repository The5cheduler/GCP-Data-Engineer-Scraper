import requests
from bs4 import BeautifulSoup

import time

def get_page_content(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
    }
    retries = 3
    for i in range(retries):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content
        elif response.status_code == 503:
            print(f"Received 503 status code. Retrying in 5 seconds... ({i+1}/{retries})")
            time.sleep(10)
        else:
            raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")
    raise Exception(f"Failed to fetch the page after {retries} retries.")

def scrape_data(url):
    page_content = get_page_content(url)
    soup = BeautifulSoup(page_content, 'html.parser')
    print(extract_question_and_answers(soup))

def extract_question_and_answers(soup):
    question_card = soup.findAll('div', class_='card exam-question-card')
    for question in question_card:
        question_number = question.find('div', class_='card-header').text.strip().split()[1]
        question_topic = question.find('span', class_='question-title-topic').text.strip()
        question_text = question.find('div', class_='card-body').p.text.strip()
        answer_choices = {}
        for choice in question.find_all('li', class_='multi-choice-item'):
            answer_letter = choice.find('span', class_='multi-choice-letter').text.strip().replace('.', '')
            answer_text = choice.text.strip().strip().replace('\n', ' ').replace('\r', '').strip().replace('  ', '').replace(answer_letter, '').replace('. ','')
            answer_choices[answer_letter]= answer_text
        return question_number, question_topic, question_text, answer_choices

if __name__ == "__main__":
    url = "https://www.examtopics.com/exams/google/professional-data-engineer/view/"
    scrape_data(url)

