import requests
from bs4 import BeautifulSoup
import threading
import time
import json
import re

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

def extract_question_and_answers(soup):
    soup = BeautifulSoup('<span class="badge badge-secondary">' + soup, 'html.parser')    
    question_num = soup.find('span', {'class': 'badge badge-secondary'}).text.strip().split(' ')[-1]   
    question_text = ""
    choices = []
    correct_answer = []
    explanation = ""
    topic = ""

    topic_elem = soup.select_one('i')
    if topic_elem is not None:
        topic = topic_elem.text.strip().replace('(', '').replace(')', '')

    br_tags = soup.select('br')
    if topic == 'Case Studies':
        # question_text = ""
        # if len(br_tags) > 1:
        #     for i in range(1, len(br_tags)-1):
        #         text = str(br_tags[i].next_sibling)
        #         if br_tags[i].next_sibling is not None and br_tags[i].next_sibling.name == 'b':
        #             text = br_tags[i].next_sibling.text
        #         question_text += text
        # question_text = question_text.split("(Case Studies)")[0].strip()
        # question_text = re.sub('<[^<]+?>', '', question_text).strip()
        # Combine the text from <br> and <b> tags
        # Extract all text between <br> tags and <b> tags in an orderly manner
        br_text = [tag.text for tag in soup.findAll('br')] if soup else []
        b_text = [tag for tag in soup.findAll('b')] if soup else []
        if len(b_text) > 1:
            b_text = b_text[:10]
            if len(b_text) > 1:
                b_text = b_text[:10]
                question_text = "\n".join([f"{b.text.strip()} {br_text[i].text.strip()}" for i, b in enumerate(b_text)])
            else:
                question_text = br_text[0].previous_sibling.strip()
    else:
        question_text = br_tags[2].previous_sibling
        if question_text is not None:
            question_text = str(question_text).strip()

    btn_group_toggle = soup.select_one('.btn-group-toggle')
    if btn_group_toggle is not None:
        choices = [choice.text.strip() for choice in btn_group_toggle.select('.alert-secondary')]
        correct_answer = [choice.text.strip() for choice in btn_group_toggle.select('.alert-secondary[value="1"]')]

    explanation_elem = soup.select_one('.collapse .card-body')
    if explanation_elem is not None:
        explanation = explanation_elem.text.strip().replace('\\r\\n\\r\\n\\r\\n', '').replace('\\r\\n', '').replace('\nA', '').replace('\\r\\n\\r\\n', '').replace('\\n','').replace('\\\'t','').replace(' we\\xe2\\x80\\x99ll ', '')


    if len(choices) > 1:
        return { 'no' : question_num, 
            'text': question_text, 
            'choices':choices, 
            'answer' : correct_answer, 
            'expanation' : explanation.strip(), 
            'topic' : topic
        }


    
def scrape_data(url):
    page_content = get_page_content(url)
    question_data_list = str(page_content).split('<span class="badge badge-secondary">')
    question_data_list = question_data_list[1:]

    result = {}
    
    for question_data in question_data_list:
        data = extract_question_and_answers(question_data)
        if data is not None:
            result[data['no']] = data
    return result

if __name__ == "__main__":
    final_result = []
    for i in range(1, 25):
        url = f"https://www.passnexam.com/google/google-data-engineer/{i}"
        single_page_date = scrape_data(url)
        final_result.append(single_page_date)
    json.dump(final_result, open('GCP_DE_questions.json', 'w'), indent=4)

