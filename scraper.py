import requests
from bs4 import BeautifulSoup

def get_page_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")

def scrape_data(url):
    page_content = get_page_content(url)
    soup = BeautifulSoup(page_content, 'html.parser')

    # Find the relevant elements and extract the data
    # Modify these selectors according to the website's structure
    exam_title = soup.select_one('h1[class="page-header"]').text.strip()
    exam_code = soup.select_one('div[class="text-muted mb-3"]').text.strip()
    
    # Assuming the content is inside a table with class "table"
    table = soup.find('table', class_='table')
    data = []
    if table:
        rows = table.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 2:
                key = cols[0].text.strip()
                value = cols[1].text.strip()
                data.append((key, value))

    return exam_title, exam_code, data

if __name__ == "__main__":
    url = "https://www.examtopics.com/exams/google/professional-data-engineer/view/"
    exam_title, exam_code, data = scrape_data(url)
    print(f"Exam Title: {exam_title}")
    print(f"Exam Code: {exam_code}")
    print("Exam Details:")
    for key, value in data:
        print(f"{key}: {value}")
