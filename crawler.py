import requests
from bs4 import BeautifulSoup


def bbc_crawler():
    url = 'http://www.bbc.com/news/world'
    source_code = requests.get(url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text)
    for link in soup.findAll('a', {'class': 'title-link'}):
        href = 'http://www.bbc.com' + link.get('href')
        print(href)
        span = link.find('h3').find('span')
        print span.string
        bbc_getContent(href)

def bbc_getContent(item_url):
    source_code = requests.get(item_url)
    plain_text = source_code.text
    soup = BeautifulSoup(plain_text)
    for title in soup.findAll('p', {'class' : 'story-body__introduction'}):
        print title.text
    for title in soup.findAll('p', {'class' : ''}):
        cls = title.attrs.get("class")
        if not cls:
            print title.text

bbc_crawler()