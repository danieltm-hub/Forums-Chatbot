import requests
import re

from queue import Queue
from bs4 import BeautifulSoup

from src.crawler.utils import ForumPage


def fetch_page(url:str) -> str | None:

    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions as e:
        print(f"Error al acceder a {url}: {e}")
        return None
    
def parse_page(html:str, page:ForumPage) -> list[ForumPage]:

    soup = BeautifulSoup(html, "html.parser")

    links = []
    for link in soup.find_all('a', href=True):
        
        url = link['href']
        
        new_page = ForumPage(url) if page.is_category() else ForumPage(url, page.main_class, page.sub_class)
        
        links.append(new_page)

    return links

def save_html(content:str, page:ForumPage):

    if not page.is_topic():
        return

    folder = f"./{page.main_class}/{page.sub_class}/"
    filename = "_".join(page.url.split("/")[-2:])

    with open(folder + filename, "w", encoding='utf-8') as f:
        f.write(content)

def download_web_page(page:ForumPage, visited_urls:set) -> list[ForumPage]:

    if page.url not in visited_urls and page.url:
        visited_urls.add(page.url)
        
        response = fetch_page(page.url)
        
        if response == None:
            return []
        
        save_html(response, page)
        
        return parse_page(response, page)

def main(first_page:str, visited_urls:set[str]):

    q = Queue(0)
    q.put(ForumPage(first_page))

    while not q.empty:
        url = q.get()
        for x in download_web_page(url, visited_urls):
            q.put(x)